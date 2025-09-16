"""
Rutas para Manejo de Envío - Sistema completo de envío
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db
from core.security import get_current_user
from features.users.models import User
from features.ecommerce.shipping_service import ShippingService
from features.ecommerce.schemas import (
    ShippingCalculationRequest, ShippingCalculationResponse,
    ShippingTotalRequest, ShippingTotalResponse,
    ShippingConfigResponse, ShippingMethod
)
import logging

logger = logging.getLogger(__name__)

shipping_router = APIRouter()

# Instancia del servicio de envío
shipping_service = ShippingService()

# === CÁLCULO DE ENVÍO ===

@shipping_router.post("/calculate", response_model=ShippingCalculationResponse)
async def calculate_shipping(
    request: ShippingCalculationRequest,
    db: Session = Depends(get_db)
):
    """
    Calcular opciones de envío para un código postal
    
    - Valida código postal
    - Calcula métodos disponibles
    - Incluye costos y fechas de entrega
    - Maneja envío gratis por umbral
    """
    try:
        result = shipping_service.calculate_shipping(
            zip_code=request.zip_code,
            cart_total=request.cart_total,
            selected_method=request.selected_method,
            delivery_date=request.delivery_date
        )
        
        return ShippingCalculationResponse(**result)
        
    except Exception as e:
        logger.error(f"Error calculating shipping: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al calcular envío: {str(e)}"
        )

@shipping_router.post("/total", response_model=ShippingTotalResponse)
async def calculate_total_with_shipping(
    request: ShippingTotalRequest,
    db: Session = Depends(get_db)
):
    """
    Calcular total incluyendo envío
    
    - Calcula costo de envío
    - Retorna total antes de impuestos
    - Incluye información del método seleccionado
    """
    try:
        result = shipping_service.calculate_total_with_shipping(
            subtotal=request.subtotal,
            shipping_method_id=request.shipping_method_id,
            zip_code=request.zip_code,
            cart_total=request.cart_total
        )
        
        return ShippingTotalResponse(**result)
        
    except Exception as e:
        logger.error(f"Error calculating total with shipping: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al calcular total con envío: {str(e)}"
        )

# === MÉTODOS DE ENVÍO ===

@shipping_router.get("/methods", response_model=List[ShippingMethod])
async def get_shipping_methods(db: Session = Depends(get_db)):
    """Obtener todos los métodos de envío disponibles"""
    try:
        methods = []
        for method_id, method_config in shipping_service.shipping_methods.items():
            if method_config["enabled"]:
                method = ShippingMethod(
                    id=method_id,
                    title=method_config["title"],
                    description=method_config["description"],
                    cost=method_config["cost"],
                    free=False,  # Se calculará dinámicamente
                    delivery_days=method_config.get("delivery_days", 1),
                    delivery_date="",  # Se calculará dinámicamente
                    delivery_time="",  # Se calculará dinámicamente
                    available=True
                )
                methods.append(method)
        
        return methods
        
    except Exception as e:
        logger.error(f"Error getting shipping methods: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener métodos de envío: {str(e)}"
        )

@shipping_router.get("/methods/{method_id}")
async def get_shipping_method(
    method_id: str,
    db: Session = Depends(get_db)
):
    """Obtener información de un método de envío específico"""
    try:
        method = shipping_service.get_shipping_method(method_id)
        
        if not method:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Shipping method '{method_id}' not found"
            )
        
        return method
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting shipping method: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener método de envío: {str(e)}"
        )

@shipping_router.post("/validate-method")
async def validate_shipping_method(
    method_id: str,
    zip_code: str,
    db: Session = Depends(get_db)
):
    """Validar si un método de envío está disponible para un código postal"""
    try:
        is_valid, message = shipping_service.validate_shipping_method(method_id, zip_code)
        
        return {
            "valid": is_valid,
            "message": message,
            "method_id": method_id,
            "zip_code": zip_code
        }
        
    except Exception as e:
        logger.error(f"Error validating shipping method: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al validar método de envío: {str(e)}"
        )

# === CONFIGURACIÓN DE ENVÍO ===

@shipping_router.get("/config", response_model=ShippingConfigResponse)
async def get_shipping_config(db: Session = Depends(get_db)):
    """Obtener configuración actual de envío"""
    try:
        config = shipping_service.get_shipping_config()
        return ShippingConfigResponse(**config)
        
    except Exception as e:
        logger.error(f"Error getting shipping config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener configuración: {str(e)}"
        )

@shipping_router.put("/config")
async def update_shipping_config(
    config_updates: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar configuración de envío (requiere autenticación)"""
    try:
        success = shipping_service.update_shipping_config(config_updates)
        
        if success:
            return {"message": "Shipping configuration updated successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error updating shipping configuration"
            )
            
    except Exception as e:
        logger.error(f"Error updating shipping config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar configuración: {str(e)}"
        )

# === ENDPOINTS DE UTILIDAD ===

@shipping_router.get("/valid-zip-codes")
async def get_valid_zip_codes(db: Session = Depends(get_db)):
    """Obtener lista de códigos postales válidos para envío"""
    try:
        return {
            "valid_zip_codes": shipping_service.valid_zip_codes,
            "total_count": len(shipping_service.valid_zip_codes)
        }
    except Exception as e:
        logger.error(f"Error getting valid zip codes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener códigos postales válidos: {str(e)}"
        )

@shipping_router.get("/free-shipping-threshold")
async def get_free_shipping_threshold(db: Session = Depends(get_db)):
    """Obtener umbral para envío gratis"""
    try:
        return {
            "free_shipping_enabled": shipping_service.shipping_config["free_shipping_enabled"],
            "free_shipping_threshold": shipping_service.shipping_config["free_shipping_threshold"],
            "default_method": shipping_service.shipping_config["default_method"]
        }
    except Exception as e:
        logger.error(f"Error getting free shipping threshold: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener umbral de envío gratis: {str(e)}"
        )

# === SINCRONIZACIÓN CON WOOCOMMERCE ===

@shipping_router.post("/sync-wc")
async def sync_with_woocommerce(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Sincronizar configuración de envío con WooCommerce
    
    - Obtiene métodos de envío reales de WooCommerce
    - Actualiza costos y configuraciones
    - Requiere autenticación
    """
    try:
        from features.ecommerce.woocommerce_proxy import WooCommerceProxy
        woo_proxy = WooCommerceProxy()
        
        success = await shipping_service.sync_with_woocommerce_shipping(woo_proxy)
        
        if success:
            return {
                "message": "Shipping configuration synced with WooCommerce successfully",
                "synced": True
            }
        else:
            return {
                "message": "No shipping methods found in WooCommerce, using defaults",
                "synced": False
            }
            
    except Exception as e:
        logger.error(f"Error syncing with WooCommerce: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al sincronizar con WooCommerce: {str(e)}"
        )

@shipping_router.get("/wc-config")
async def get_woocommerce_shipping_config(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener configuración de envío de WooCommerce
    
    - Muestra métodos configurados en WooCommerce
    - Incluye costos y configuraciones reales
    - Requiere autenticación
    """
    try:
        from features.ecommerce.woocommerce_proxy import WooCommerceProxy
        woo_proxy = WooCommerceProxy()
        
        wc_config = await shipping_service.get_wc_shipping_config(woo_proxy)
        
        return {
            "woocommerce_config": wc_config,
            "current_local_config": shipping_service.get_shipping_config()
        }
        
    except Exception as e:
        logger.error(f"Error getting WooCommerce config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener configuración de WooCommerce: {str(e)}"
        )

@shipping_router.get("/wc-methods")
async def get_woocommerce_shipping_methods(db: Session = Depends(get_db)):
    """
    Obtener métodos de envío de WooCommerce (público)
    
    - Muestra métodos disponibles en WooCommerce
    - Útil para debugging y verificación
    """
    try:
        from features.ecommerce.woocommerce_proxy import WooCommerceProxy
        woo_proxy = WooCommerceProxy()
        
        wc_config = await woo_proxy.get_all_shipping_methods()
        
        # Formatear para respuesta más clara
        formatted_methods = []
        for zone in wc_config.get("zones", []):
            for method in zone.get("methods", []):
                formatted_methods.append({
                    "zone_name": zone.get("name"),
                    "zone_id": zone.get("id"),
                    "method_id": method.get("method_id"),
                    "title": method.get("title"),
                    "cost": method.get("cost"),
                    "enabled": method.get("enabled"),
                    "tax_status": method.get("tax_status"),
                    "settings": method.get("settings", {})
                })
        
        return {
            "woocommerce_methods": formatted_methods,
            "total_methods": len(formatted_methods),
            "zones": wc_config.get("zones", [])
        }
        
    except Exception as e:
        logger.error(f"Error getting WooCommerce methods: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener métodos de WooCommerce: {str(e)}"
        )

# === STORE PICKUP ===

@shipping_router.post("/store-pickup/calculate")
async def calculate_store_pickup(
    cart_total: float,
    db: Session = Depends(get_db)
):
    """
    Calcular opciones para Store Pickup
    
    - Solo método local_pickup disponible
    - Sin validación de código postal
    - Costo siempre $0.00
    """
    try:
        result = shipping_service.calculate_shipping(
            zip_code="00000",  # Dummy zip para pickup
            cart_total=cart_total,
            selected_method="local_pickup",
            is_store_pickup=True
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error calculating store pickup: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al calcular Store Pickup: {str(e)}"
        )

@shipping_router.post("/store-pickup/validate")
async def validate_store_pickup_info(
    billing_info: dict,
    db: Session = Depends(get_db)
):
    """
    Validar información requerida para Store Pickup
    
    - Solo requiere datos básicos de facturación
    - No requiere dirección de envío
    """
    try:
        from features.ecommerce.validation_service import ValidationService
        validation_service = ValidationService()
        
        # Validar campos básicos para pickup
        required_fields = [
            ("billing_first_name", "Nombre"),
            ("billing_last_name", "Apellido"),
            ("billing_email", "Email"),
            ("billing_phone", "Teléfono")
        ]
        
        errors = []
        for field_key, field_name in required_fields:
            if not billing_info.get(field_key, "").strip():
                errors.append(f"{field_name} es requerido para recogida en tienda")
        
        # Validar email
        email = billing_info.get("billing_email", "")
        if email and "@" not in email:
            errors.append("Email no válido")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "required_fields": ["billing_first_name", "billing_last_name", "billing_email", "billing_phone"],
            "optional_fields": ["billing_address_1", "billing_city", "billing_state", "billing_postcode"]
        }
        
    except Exception as e:
        logger.error(f"Error validating store pickup info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al validar información de Store Pickup: {str(e)}"
        )

@shipping_router.get("/store-pickup/info")
async def get_store_pickup_info(db: Session = Depends(get_db)):
    """
    Obtener información de Store Pickup
    
    - Horarios de atención
    - Ubicación de la tienda
    - Instrucciones para recogida
    """
    try:
        return {
            "store_name": "Flowers Freehold",
            "store_address": {
                "street": "123 Main Street",
                "city": "Freehold",
                "state": "NJ",
                "zip_code": "07728",
                "country": "US"
            },
            "business_hours": {
                "monday": "9:00 AM - 6:00 PM",
                "tuesday": "9:00 AM - 6:00 PM",
                "wednesday": "9:00 AM - 6:00 PM",
                "thursday": "9:00 AM - 6:00 PM",
                "friday": "9:00 AM - 7:00 PM",
                "saturday": "9:00 AM - 5:00 PM",
                "sunday": "Closed"
            },
            "pickup_instructions": [
                "Presentar identificación válida",
                "Mostrar confirmación de orden en el teléfono",
                "Recoger dentro de 7 días hábiles",
                "Contactar tienda si necesita más tiempo"
            ],
            "contact_info": {
                "phone": "(555) 123-4567",
                "email": "info@flowersfreehold.com"
            },
            "pickup_method": {
                "id": "local_pickup",
                "title": "Store Pickup",
                "description": "Pick up at our store location",
                "cost": 0.00,
                "free": True,
                "delivery_days": 0,
                "delivery_date": "Same day",
                "delivery_time": "Same day pickup",
                "available": True
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting store pickup info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener información de Store Pickup: {str(e)}"
        )

# === ENDPOINT DE PRUEBA ===

@shipping_router.post("/test-calculation")
async def test_shipping_calculation(
    zip_code: str = "07728",
    cart_total: float = 54.99,
    method_id: str = "flat_rate",
    db: Session = Depends(get_db)
):
    """
    Endpoint de prueba para cálculo de envío
    Útil para testing y debugging
    """
    try:
        # Calcular opciones de envío
        shipping_options = shipping_service.calculate_shipping(
            zip_code=zip_code,
            cart_total=cart_total,
            selected_method=method_id
        )
        
        # Calcular total con envío
        total_with_shipping = shipping_service.calculate_total_with_shipping(
            subtotal=cart_total,
            shipping_method_id=method_id,
            zip_code=zip_code,
            cart_total=cart_total
        )
        
        return {
            "test_data": {
                "zip_code": zip_code,
                "cart_total": cart_total,
                "method_id": method_id
            },
            "shipping_options": shipping_options,
            "total_with_shipping": total_with_shipping
        }
        
    except Exception as e:
        logger.error(f"Error in test calculation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en cálculo de prueba: {str(e)}"
        )
