"""
Servicio de Cálculo de Impuestos - Manejo completo de impuestos para e-commerce
"""
import httpx
import os
from typing import Dict, List, Optional, Tuple, Any
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TaxService:
    """Servicio centralizado para cálculo de impuestos"""
    
    def __init__(self):
        # Configuración de impuestos por estado (US)
        self.state_tax_rates = {
            "AL": {"rate": 0.04, "name": "Alabama"},
            "AK": {"rate": 0.00, "name": "Alaska"},
            "AZ": {"rate": 0.056, "name": "Arizona"},
            "AR": {"rate": 0.065, "name": "Arkansas"},
            "CA": {"rate": 0.0725, "name": "California"},
            "CO": {"rate": 0.029, "name": "Colorado"},
            "CT": {"rate": 0.0635, "name": "Connecticut"},
            "DE": {"rate": 0.00, "name": "Delaware"},
            "FL": {"rate": 0.06, "name": "Florida"},
            "GA": {"rate": 0.04, "name": "Georgia"},
            "HI": {"rate": 0.04, "name": "Hawaii"},
            "ID": {"rate": 0.06, "name": "Idaho"},
            "IL": {"rate": 0.0625, "name": "Illinois"},
            "IN": {"rate": 0.07, "name": "Indiana"},
            "IA": {"rate": 0.06, "name": "Iowa"},
            "KS": {"rate": 0.065, "name": "Kansas"},
            "KY": {"rate": 0.06, "name": "Kentucky"},
            "LA": {"rate": 0.0445, "name": "Louisiana"},
            "ME": {"rate": 0.055, "name": "Maine"},
            "MD": {"rate": 0.06, "name": "Maryland"},
            "MA": {"rate": 0.0625, "name": "Massachusetts"},
            "MI": {"rate": 0.06, "name": "Michigan"},
            "MN": {"rate": 0.06875, "name": "Minnesota"},
            "MS": {"rate": 0.07, "name": "Mississippi"},
            "MO": {"rate": 0.04225, "name": "Missouri"},
            "MT": {"rate": 0.00, "name": "Montana"},
            "NE": {"rate": 0.055, "name": "Nebraska"},
            "NV": {"rate": 0.0685, "name": "Nevada"},
            "NH": {"rate": 0.00, "name": "New Hampshire"},
            "NJ": {"rate": 0.06625, "name": "New Jersey"},
            "NM": {"rate": 0.05125, "name": "New Mexico"},
            "NY": {"rate": 0.08, "name": "New York"},
            "NC": {"rate": 0.0475, "name": "North Carolina"},
            "ND": {"rate": 0.05, "name": "North Dakota"},
            "OH": {"rate": 0.0575, "name": "Ohio"},
            "OK": {"rate": 0.045, "name": "Oklahoma"},
            "OR": {"rate": 0.00, "name": "Oregon"},
            "PA": {"rate": 0.06, "name": "Pennsylvania"},
            "RI": {"rate": 0.07, "name": "Rhode Island"},
            "SC": {"rate": 0.06, "name": "South Carolina"},
            "SD": {"rate": 0.045, "name": "South Dakota"},
            "TN": {"rate": 0.07, "name": "Tennessee"},
            "TX": {"rate": 0.0625, "name": "Texas"},
            "UT": {"rate": 0.0485, "name": "Utah"},
            "VT": {"rate": 0.06, "name": "Vermont"},
            "VA": {"rate": 0.053, "name": "Virginia"},
            "WA": {"rate": 0.065, "name": "Washington"},
            "WV": {"rate": 0.06, "name": "West Virginia"},
            "WI": {"rate": 0.05, "name": "Wisconsin"},
            "WY": {"rate": 0.04, "name": "Wyoming"},
            "DC": {"rate": 0.06, "name": "District of Columbia"}
        }
        
        # Impuestos locales por código postal (ejemplos para NJ)
        self.local_tax_rates = {
            "07728": {"rate": 0.0, "name": "Middletown Township"},
            "08527": {"rate": 0.0, "name": "Cranbury Township"},
            "07731": {"rate": 0.0, "name": "Holmdel Township"},
            "07727": {"rate": 0.0, "name": "Hazlet Township"},
            "07722": {"rate": 0.0, "name": "Freehold Township"},
            "07746": {"rate": 0.0, "name": "Matawan"},
            "07738": {"rate": 0.0, "name": "Keyport"},
            "08701": {"rate": 0.0, "name": "Lakewood Township"},
            "07721": {"rate": 0.0, "name": "Freehold Borough"},
            "07747": {"rate": 0.0, "name": "Middletown Township"},
            # Agregar más códigos postales según necesidad
        }
        
        # Configuración de impuestos
        self.tax_config = {
            "nexus_states": ["NJ", "NY", "PA"],  # Estados donde tenemos presencia física
            "default_tax_class": "standard",
            "tax_inclusive": False,  # Los precios no incluyen impuestos
            "rounding_method": "round_half_up",
            "tax_exempt_products": [],  # SKUs de productos exentos
            "tax_exempt_customers": []  # IDs de clientes exentos
        }
    
    def calculate_tax(
        self, 
        subtotal: float, 
        shipping_address: Dict[str, str],
        billing_address: Optional[Dict[str, str]] = None,
        line_items: Optional[List[Dict[str, Any]]] = None,
        customer_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Calcular impuestos para una orden
        
        Args:
            subtotal: Subtotal de la orden
            shipping_address: Dirección de envío
            billing_address: Dirección de facturación (opcional)
            line_items: Items de la orden (opcional)
            customer_id: ID del cliente (opcional)
        
        Returns:
            Dict con información de impuestos calculados
        """
        try:
            # Verificar si el cliente está exento de impuestos
            if customer_id and customer_id in self.tax_config["tax_exempt_customers"]:
                return self._create_tax_response(subtotal, 0.0, 0.0, "Tax exempt customer")
            
            # Determinar la dirección para cálculo de impuestos
            tax_address = self._determine_tax_address(shipping_address, billing_address)
            
            # Verificar si tenemos nexus en el estado
            state = tax_address.get("state", "").upper()
            if state not in self.tax_config["nexus_states"]:
                return self._create_tax_response(subtotal, 0.0, 0.0, "No nexus in state")
            
            # Calcular impuestos estatales
            state_tax_rate = self.state_tax_rates.get(state, {}).get("rate", 0.0)
            state_tax_amount = self._calculate_tax_amount(subtotal, state_tax_rate)
            
            # Calcular impuestos locales
            zip_code = tax_address.get("postcode", "")
            local_tax_rate = self.local_tax_rates.get(zip_code, {}).get("rate", 0.0)
            local_tax_amount = self._calculate_tax_amount(subtotal, local_tax_rate)
            
            # Calcular total de impuestos
            total_tax_rate = state_tax_rate + local_tax_rate
            total_tax_amount = state_tax_amount + local_tax_amount
            
            # Crear respuesta detallada
            tax_breakdown = {
                "state_tax": {
                    "rate": state_tax_rate,
                    "amount": float(state_tax_amount),
                    "name": self.state_tax_rates.get(state, {}).get("name", f"State Tax ({state})")
                },
                "local_tax": {
                    "rate": local_tax_rate,
                    "amount": float(local_tax_amount),
                    "name": self.local_tax_rates.get(zip_code, {}).get("name", f"Local Tax ({zip_code})")
                }
            }
            
            return {
                "subtotal": subtotal,
                "total_tax_rate": total_tax_rate,
                "total_tax_amount": float(total_tax_amount),
                "tax_breakdown": tax_breakdown,
                "tax_address": tax_address,
                "nexus_state": state in self.tax_config["nexus_states"],
                "calculation_method": "backend_calculation"
            }
            
        except Exception as e:
            logger.error(f"Error calculating tax: {str(e)}")
            return self._create_tax_response(subtotal, 0.0, 0.0, f"Error: {str(e)}")
    
    def _determine_tax_address(
        self, 
        shipping_address: Dict[str, str], 
        billing_address: Optional[Dict[str, str]]
    ) -> Dict[str, str]:
        """Determinar qué dirección usar para cálculo de impuestos"""
        # Regla: usar dirección de envío si es diferente a facturación
        # Si son iguales o no hay facturación, usar envío
        if not billing_address:
            return shipping_address
        
        # Comparar direcciones (simplificado)
        shipping_key = f"{shipping_address.get('address_1', '')}{shipping_address.get('city', '')}{shipping_address.get('state', '')}"
        billing_key = f"{billing_address.get('address_1', '')}{billing_address.get('city', '')}{billing_address.get('state', '')}"
        
        if shipping_key != billing_key:
            return shipping_address
        else:
            return billing_address
    
    def _calculate_tax_amount(self, amount: float, rate: float) -> Decimal:
        """Calcular monto de impuesto con redondeo apropiado"""
        tax_amount = Decimal(str(amount)) * Decimal(str(rate))
        return tax_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    def _create_tax_response(
        self, 
        subtotal: float, 
        tax_rate: float, 
        tax_amount: float, 
        reason: str
    ) -> Dict[str, Any]:
        """Crear respuesta estándar de impuestos"""
        return {
            "subtotal": subtotal,
            "total_tax_rate": tax_rate,
            "total_tax_amount": tax_amount,
            "tax_breakdown": {},
            "tax_address": {},
            "nexus_state": False,
            "calculation_method": "backend_calculation",
            "reason": reason
        }
    
    async def validate_tax_id(self, tax_id: str, country: str = "US") -> Dict[str, Any]:
        """
        Validar Tax ID (EIN, SSN, etc.)
        
        Args:
            tax_id: Tax ID a validar
            country: País (default: US)
        
        Returns:
            Dict con resultado de validación
        """
        try:
            if country.upper() == "US":
                return self._validate_us_tax_id(tax_id)
            else:
                return {"valid": False, "error": "Country not supported"}
                
        except Exception as e:
            logger.error(f"Error validating tax ID: {str(e)}")
            return {"valid": False, "error": str(e)}
    
    def _validate_us_tax_id(self, tax_id: str) -> Dict[str, Any]:
        """Validar Tax ID de Estados Unidos"""
        # Limpiar tax_id
        clean_tax_id = tax_id.replace("-", "").replace(" ", "")
        
        # Validar formato básico
        if not clean_tax_id.isdigit():
            return {"valid": False, "error": "Tax ID must contain only numbers"}
        
        # EIN (Employer Identification Number) - 9 dígitos
        if len(clean_tax_id) == 9:
            return self._validate_ein(clean_tax_id)
        
        # SSN (Social Security Number) - 9 dígitos
        elif len(clean_tax_id) == 9:
            return self._validate_ssn(clean_tax_id)
        
        else:
            return {"valid": False, "error": "Invalid Tax ID length"}
    
    def _validate_ein(self, ein: str) -> Dict[str, Any]:
        """Validar EIN"""
        # EIN no puede empezar con 0, 7, 8, 9
        if ein[0] in ['0', '7', '8', '9']:
            return {"valid": False, "error": "Invalid EIN prefix"}
        
        # EIN no puede ser 00-0000000
        if ein == "000000000":
            return {"valid": False, "error": "Invalid EIN"}
        
        return {
            "valid": True,
            "type": "EIN",
            "formatted": f"{ein[:2]}-{ein[2:]}",
            "message": "Valid EIN"
        }
    
    def _validate_ssn(self, ssn: str) -> Dict[str, Any]:
        """Validar SSN"""
        # SSN no puede empezar con 000, 666, o 9
        if ssn[:3] in ['000', '666'] or ssn[0] == '9':
            return {"valid": False, "error": "Invalid SSN prefix"}
        
        # SSN no puede ser 000-00-0000
        if ssn == "000000000":
            return {"valid": False, "error": "Invalid SSN"}
        
        return {
            "valid": True,
            "type": "SSN",
            "formatted": f"{ssn[:3]}-{ssn[3:5]}-{ssn[5:]}",
            "message": "Valid SSN"
        }
    
    def get_tax_rates_by_location(self, state: str, zip_code: Optional[str] = None) -> Dict[str, Any]:
        """Obtener tasas de impuestos por ubicación"""
        state_info = self.state_tax_rates.get(state.upper(), {})
        local_info = {}
        
        if zip_code:
            local_info = self.local_tax_rates.get(zip_code, {})
        
        return {
            "state": {
                "code": state.upper(),
                "rate": state_info.get("rate", 0.0),
                "name": state_info.get("name", f"State ({state})")
            },
            "local": {
                "zip_code": zip_code,
                "rate": local_info.get("rate", 0.0),
                "name": local_info.get("name", f"Local ({zip_code})")
            },
            "total_rate": state_info.get("rate", 0.0) + local_info.get("rate", 0.0)
        }
    
    def is_tax_exempt(self, customer_id: Optional[int] = None, product_sku: Optional[str] = None) -> bool:
        """Verificar si cliente o producto está exento de impuestos"""
        if customer_id and customer_id in self.tax_config["tax_exempt_customers"]:
            return True
        
        if product_sku and product_sku in self.tax_config["tax_exempt_products"]:
            return True
        
        return False
    
    def update_tax_config(self, config_updates: Dict[str, Any]) -> bool:
        """Actualizar configuración de impuestos"""
        try:
            self.tax_config.update(config_updates)
            logger.info(f"Tax config updated: {config_updates}")
            return True
        except Exception as e:
            logger.error(f"Error updating tax config: {str(e)}")
            return False
    
    async def sync_with_woocommerce_taxes(self, woo_proxy) -> bool:
        """Sincronizar configuración de impuestos con WooCommerce"""
        try:
            # Obtener configuración de impuestos de WooCommerce
            # Esto requeriría endpoints adicionales en WooCommerce
            # Por ahora, retornamos True como placeholder
            logger.info("Tax configuration synced with WooCommerce")
            return True
        except Exception as e:
            logger.error(f"Error syncing with WooCommerce: {str(e)}")
            return False
