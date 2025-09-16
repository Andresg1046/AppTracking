"""
Servicio de Cálculo de Envío - Manejo completo de costos de envío
"""
import httpx
import os
from typing import Dict, List, Optional, Tuple, Any
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ShippingService:
    """Servicio centralizado para cálculo de envío"""
    
    def __init__(self):
        # Configuración de métodos de envío
        self.shipping_methods = {
            "flat_rate": {
                "id": "flat_rate",
                "title": "Delivery Service",
                "description": "Standard delivery service",
                "enabled": True,
                "cost": 10.00,  # Costo base
                "free_shipping_threshold": 75.00,  # Envío gratis sobre $75
                "delivery_days": 1,  # Días de entrega
                "available_zips": "all"  # Disponible en todos los códigos postales válidos
            },
            "local_pickup": {
                "id": "local_pickup",
                "title": "Store Pickup",
                "description": "Pick up at our store location",
                "enabled": True,
                "cost": 0.00,
                "delivery_days": 0,  # Mismo día
                "available_zips": "all"
            },
            "express_delivery": {
                "id": "express_delivery",
                "title": "Express Delivery",
                "description": "Same day delivery (before 3 PM cutoff)",
                "enabled": True,
                "cost": 25.00,
                "delivery_days": 0,  # Mismo día
                "cutoff_time": 15,  # 3:00 PM
                "available_zips": "all"
            },
            "premium_delivery": {
                "id": "premium_delivery",
                "title": "Premium Delivery",
                "description": "Premium delivery with tracking",
                "enabled": True,
                "cost": 20.00,
                "delivery_days": 1,
                "available_zips": "all"
            }
        }
        
        # Códigos postales válidos (mismo que validation_service)
        self.valid_zip_codes = [
            "07728", "08527", "07731", "07727", "07722", "07746", "07738", 
            "08701", "07721", "07747", "08879", "08857", "07751", "07733", "07730", "08520", 
            "08831", "08828", "08501", "08535", "08555", "08510", "08759", "08757", "08755", "08733", 
            "08753", "08751", "08735", "08723", "08738", "08724", "08742", "08730", "08720", "08736", 
            "08750", "07762", "07719", "07753", "07717", "07720", "07711", "07723", "07755", 
            "07740", "07764", "07757", "07750", "07703", "07702", "07739", "07704", "07716", "07737", 
            "07718", "07756", "07701", "07712", "07724", "07726", "07734", "07740", "07748", "07758",
            "07760", "08512", "08514", "08535", "08816", "08872", "08884"
        ]
        
        # Configuración de envío
        self.shipping_config = {
            "default_method": "flat_rate",
            "free_shipping_enabled": True,
            "free_shipping_threshold": 75.00,
            "tax_shipping": True,  # Los envíos están sujetos a impuestos
            "delivery_cutoff_time": 15,  # 3:00 PM
            "business_days_only": True,  # Solo días hábiles
            "weekend_delivery": False  # No entregas fines de semana
        }
    
    def calculate_shipping(
        self,
        zip_code: str,
        cart_total: float,
        selected_method: Optional[str] = None,
        delivery_date: Optional[str] = None,
        is_store_pickup: bool = False
    ) -> Dict[str, Any]:
        """
        Calcular opciones de envío para un código postal
        
        Args:
            zip_code: Código postal de destino
            cart_total: Total del carrito
            selected_method: Método seleccionado (opcional)
            delivery_date: Fecha de entrega deseada (opcional)
            is_store_pickup: Si es recogida en tienda
        
        Returns:
            Dict con opciones de envío disponibles
        """
        try:
            # Si es Store Pickup, no validar código postal
            if is_store_pickup:
                if selected_method == "local_pickup":
                    # Retornar solo método de pickup
                    pickup_method = self._create_pickup_method()
                    return {
                        "selected_method": pickup_method,
                        "available_methods": [pickup_method],
                        "valid_zip": True,
                        "is_store_pickup": True
                    }
                else:
                    return {
                        "available_methods": [self._create_pickup_method()],
                        "error": "Only store pickup available for this option",
                        "valid_zip": True,
                        "is_store_pickup": True
                    }
            
            # Para envío normal, validar código postal
            if zip_code not in self.valid_zip_codes:
                return {
                    "available_methods": [],
                    "error": "Zip code not valid for delivery",
                    "valid_zip": False,
                    "is_store_pickup": False
                }
            
            # Obtener métodos disponibles (excluyendo pickup para envío normal)
            available_methods = self._get_available_methods(zip_code, cart_total, delivery_date, exclude_pickup=True)
            
            # Si se especifica un método, retornar solo ese
            if selected_method:
                method = next((m for m in available_methods if m["id"] == selected_method), None)
                if method:
                    return {
                        "selected_method": method,
                        "available_methods": available_methods,
                        "valid_zip": True,
                        "is_store_pickup": False
                    }
                else:
                    return {
                        "available_methods": available_methods,
                        "error": f"Shipping method '{selected_method}' not available",
                        "valid_zip": True,
                        "is_store_pickup": False
                    }
            
            return {
                "available_methods": available_methods,
                "valid_zip": True,
                "is_store_pickup": False
            }
            
        except Exception as e:
            logger.error(f"Error calculating shipping: {str(e)}")
            return {
                "available_methods": [],
                "error": f"Error calculating shipping: {str(e)}",
                "valid_zip": False,
                "is_store_pickup": False
            }
    
    def _create_pickup_method(self) -> Dict[str, Any]:
        """Crear método de pickup en tienda"""
        pickup_config = self.shipping_methods["local_pickup"]
        delivery_info = self._calculate_delivery_date(pickup_config)
        
        return {
            "id": "local_pickup",
            "title": pickup_config["title"],
            "description": pickup_config["description"],
            "cost": 0.0,
            "free": True,
            "delivery_days": 0,
            "delivery_date": delivery_info["delivery_date"],
            "delivery_time": delivery_info["delivery_time"],
            "available": True
        }
    
    def _get_available_methods(
        self, 
        zip_code: str, 
        cart_total: float, 
        delivery_date: Optional[str] = None,
        exclude_pickup: bool = False
    ) -> List[Dict[str, Any]]:
        """Obtener métodos de envío disponibles"""
        available_methods = []
        
        for method_id, method_config in self.shipping_methods.items():
            if not method_config["enabled"]:
                continue
            
            # Excluir pickup si se solicita
            if exclude_pickup and method_id == "local_pickup":
                continue
            
            # Verificar disponibilidad por código postal
            if method_config["available_zips"] != "all":
                if zip_code not in method_config["available_zips"]:
                    continue
            
            # Calcular costo
            cost = self._calculate_method_cost(method_config, cart_total)
            
            # Calcular fecha de entrega
            delivery_info = self._calculate_delivery_date(method_config, delivery_date)
            
            # Crear método de envío
            shipping_method = {
                "id": method_id,
                "title": method_config["title"],
                "description": method_config["description"],
                "cost": cost,
                "free": cost == 0.0,
                "delivery_days": method_config.get("delivery_days", 1),
                "delivery_date": delivery_info["delivery_date"],
                "delivery_time": delivery_info["delivery_time"],
                "available": True
            }
            
            available_methods.append(shipping_method)
        
        return available_methods
    
    def _calculate_method_cost(self, method_config: Dict[str, Any], cart_total: float) -> float:
        """Calcular costo del método de envío"""
        base_cost = method_config["cost"]
        
        # Verificar envío gratis
        if self.shipping_config["free_shipping_enabled"]:
            free_threshold = method_config.get("free_shipping_threshold", self.shipping_config["free_shipping_threshold"])
            if cart_total >= free_threshold:
                return 0.0
        
        return base_cost
    
    def _calculate_delivery_date(self, method_config: Dict[str, Any], requested_date: Optional[str] = None) -> Dict[str, Any]:
        """Calcular fecha de entrega para un método"""
        try:
            current_time = datetime.now()
            
            # Si es pickup local, mismo día
            if method_config["id"] == "local_pickup":
                return {
                    "delivery_date": current_time.strftime("%A, %B %d, %Y"),
                    "delivery_time": "Same day pickup"
                }
            
            # Si es express delivery, verificar cutoff time
            if method_config["id"] == "express_delivery":
                cutoff_time = method_config.get("cutoff_time", self.shipping_config["delivery_cutoff_time"])
                cutoff_datetime = current_time.replace(hour=cutoff_time, minute=0, second=0, microsecond=0)
                
                if current_time > cutoff_datetime:
                    # Ya pasó la hora límite, entregar al día siguiente
                    delivery_date = current_time + timedelta(days=1)
                else:
                    # Entregar el mismo día
                    delivery_date = current_time
                
                return {
                    "delivery_date": delivery_date.strftime("%A, %B %d, %Y"),
                    "delivery_time": "Same day delivery"
                }
            
            # Métodos estándar
            delivery_days = method_config.get("delivery_days", 1)
            delivery_date = current_time + timedelta(days=delivery_days)
            
            # Ajustar para días hábiles si es necesario
            if self.shipping_config["business_days_only"]:
                while delivery_date.weekday() >= 5:  # Sábado = 5, Domingo = 6
                    delivery_date += timedelta(days=1)
            
            return {
                "delivery_date": delivery_date.strftime("%A, %B %d, %Y"),
                "delivery_time": f"{delivery_days} business day(s)"
            }
            
        except Exception as e:
            logger.error(f"Error calculating delivery date: {str(e)}")
            return {
                "delivery_date": "Unable to calculate",
                "delivery_time": "Contact for details"
            }
    
    def get_shipping_method(self, method_id: str) -> Optional[Dict[str, Any]]:
        """Obtener información de un método de envío específico"""
        return self.shipping_methods.get(method_id)
    
    def validate_shipping_method(self, method_id: str, zip_code: str) -> Tuple[bool, str]:
        """Validar si un método de envío está disponible para un código postal"""
        method = self.shipping_methods.get(method_id)
        
        if not method:
            return False, f"Shipping method '{method_id}' not found"
        
        if not method["enabled"]:
            return False, f"Shipping method '{method_id}' is disabled"
        
        if zip_code not in self.valid_zip_codes:
            return False, "Zip code not valid for delivery"
        
        if method["available_zips"] != "all" and zip_code not in method["available_zips"]:
            return False, f"Shipping method '{method_id}' not available for zip code {zip_code}"
        
        return True, "Valid"
    
    def calculate_total_with_shipping(
        self,
        subtotal: float,
        shipping_method_id: str,
        zip_code: str,
        cart_total: Optional[float] = None
    ) -> Dict[str, Any]:
        """Calcular total incluyendo envío"""
        try:
            if cart_total is None:
                cart_total = subtotal
            
            # Calcular costo de envío
            shipping_info = self.calculate_shipping(zip_code, cart_total, shipping_method_id)
            
            if not shipping_info["valid_zip"]:
                return {
                    "subtotal": subtotal,
                    "shipping_cost": 0.0,
                    "total_before_tax": subtotal,
                    "error": shipping_info.get("error", "Invalid zip code")
                }
            
            selected_method = shipping_info.get("selected_method")
            if not selected_method:
                return {
                    "subtotal": subtotal,
                    "shipping_cost": 0.0,
                    "total_before_tax": subtotal,
                    "error": "Shipping method not available"
                }
            
            shipping_cost = selected_method["cost"]
            total_before_tax = subtotal + shipping_cost
            
            return {
                "subtotal": subtotal,
                "shipping_cost": shipping_cost,
                "shipping_method": selected_method,
                "total_before_tax": total_before_tax,
                "shipping_taxable": self.shipping_config["tax_shipping"]
            }
            
        except Exception as e:
            logger.error(f"Error calculating total with shipping: {str(e)}")
            return {
                "subtotal": subtotal,
                "shipping_cost": 0.0,
                "total_before_tax": subtotal,
                "error": f"Error: {str(e)}"
            }
    
    def update_shipping_config(self, config_updates: Dict[str, Any]) -> bool:
        """Actualizar configuración de envío"""
        try:
            self.shipping_config.update(config_updates)
            logger.info(f"Shipping config updated: {config_updates}")
            return True
        except Exception as e:
            logger.error(f"Error updating shipping config: {str(e)}")
            return False
    
    def get_shipping_config(self) -> Dict[str, Any]:
        """Obtener configuración actual de envío"""
        return {
            "shipping_methods": self.shipping_methods,
            "shipping_config": self.shipping_config,
            "valid_zip_codes": self.valid_zip_codes
        }
    
    async def sync_with_woocommerce_shipping(self, woo_proxy) -> bool:
        """Sincronizar configuración de envío con WooCommerce"""
        try:
            # Obtener métodos de envío de WooCommerce
            wc_shipping_config = await woo_proxy.get_all_shipping_methods()
            
            if wc_shipping_config and wc_shipping_config.get("methods"):
                # Actualizar métodos de envío con datos reales de WooCommerce
                self._update_shipping_methods_from_wc(wc_shipping_config)
                logger.info("Shipping configuration synced with WooCommerce")
                return True
            else:
                logger.warning("No shipping methods found in WooCommerce, using defaults")
                return False
                
        except Exception as e:
            logger.error(f"Error syncing with WooCommerce: {str(e)}")
            return False
    
    def _update_shipping_methods_from_wc(self, wc_config: Dict[str, Any]) -> None:
        """Actualizar métodos de envío con datos de WooCommerce"""
        try:
            wc_methods = wc_config.get("methods", {})
            
            # Buscar método "flat_rate" (Delivery Service)
            for method_key, method_data in wc_methods.items():
                method_id = method_data.get("method_id")
                
                if method_id == "flat_rate":
                    # Actualizar flat_rate con datos reales
                    cost_str = method_data.get("cost", "10")
                    try:
                        cost = float(cost_str)
                    except ValueError:
                        cost = 10.0
                    
                    self.shipping_methods["flat_rate"].update({
                        "title": method_data.get("title", "Delivery Service"),
                        "cost": cost,
                        "enabled": method_data.get("enabled", True),
                        "tax_status": method_data.get("tax_status", "taxable")
                    })
                    
                    logger.info(f"Updated flat_rate method: cost=${cost}, title='{method_data.get('title')}'")
                
                elif method_id == "local_pickup":
                    # Actualizar local_pickup
                    self.shipping_methods["local_pickup"].update({
                        "title": method_data.get("title", "Store Pickup"),
                        "enabled": method_data.get("enabled", True),
                        "tax_status": method_data.get("tax_status", "taxable")
                    })
                    
                    logger.info(f"Updated local_pickup method: title='{method_data.get('title')}'")
            
            # Actualizar configuración de impuestos si es necesario
            if wc_config.get("settings"):
                settings = wc_config["settings"]
                if "tax_shipping" in settings:
                    self.shipping_config["tax_shipping"] = settings["tax_shipping"]
                    
        except Exception as e:
            logger.error(f"Error updating shipping methods from WooCommerce: {str(e)}")
    
    async def get_wc_shipping_config(self, woo_proxy) -> Dict[str, Any]:
        """Obtener configuración de envío de WooCommerce"""
        try:
            wc_config = await woo_proxy.get_all_shipping_methods()
            return wc_config
        except Exception as e:
            logger.error(f"Error getting WooCommerce shipping config: {str(e)}")
            return {"zones": [], "methods": {}, "settings": {}}
