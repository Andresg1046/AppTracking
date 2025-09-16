"""
Rutas para Checkout Multi-Paso - Reemplaza la funcionalidad del plugin WordPress
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db
from core.security import get_current_user
from features.users.models import User
from features.ecommerce.checkout_service import CheckoutService
from features.ecommerce.schemas import (
    CheckoutStep1Request, CheckoutStep1Response,
    CheckoutStep2Request, CheckoutStep2Response,
    CheckoutStep3Request, CheckoutStep3Response,
    ZipCodeValidationRequest, ZipCodeValidationResponse,
    DeliveryDateRequest, DeliveryDateResponse,
    CheckoutValidationRequest, CheckoutValidationResponse,
    OrderResponse
)
from features.ecommerce.models import Order
import logging

logger = logging.getLogger(__name__)

checkout_router = APIRouter()

# Instancia del servicio de checkout
checkout_service = CheckoutService()

# === VALIDACIONES INDIVIDUALES ===

@checkout_router.post("/validate-zip", response_model=ZipCodeValidationResponse)
async def validate_zip_code(
    request: ZipCodeValidationRequest,
    db: Session = Depends(get_db)
):
    """Validar código postal individualmente"""
    try:
        return await checkout_service.validate_zip_code(request)
    except Exception as e:
        logger.error(f"Error validating zip code: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al validar código postal: {str(e)}"
        )

@checkout_router.post("/delivery-dates", response_model=DeliveryDateResponse)
async def get_delivery_dates(
    request: DeliveryDateRequest,
    db: Session = Depends(get_db)
):
    """Obtener fechas de entrega disponibles"""
    try:
        return await checkout_service.get_delivery_dates(request)
    except Exception as e:
        logger.error(f"Error getting delivery dates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener fechas de entrega: {str(e)}"
        )

@checkout_router.post("/validate-step", response_model=CheckoutValidationResponse)
async def validate_checkout_step(
    request: CheckoutValidationRequest,
    db: Session = Depends(get_db)
):
    """Validar un paso específico del checkout"""
    try:
        return await checkout_service.validate_checkout_step(request)
    except Exception as e:
        logger.error(f"Error validating checkout step: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al validar paso del checkout: {str(e)}"
        )

# === CHECKOUT MULTI-PASO ===

@checkout_router.post("/step1", response_model=CheckoutStep1Response)
async def process_checkout_step1(
    request: CheckoutStep1Request,
    db: Session = Depends(get_db)
):
    """
    Paso 1: Validar información de envío
    - Validar código postal
    - Validar campos requeridos
    - Calcular fecha de entrega
    - Obtener información de ubicación
    """
    try:
        return await checkout_service.process_step1(request)
    except Exception as e:
        logger.error(f"Error processing checkout step 1: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar paso 1: {str(e)}"
        )

@checkout_router.post("/step2", response_model=CheckoutStep2Response)
async def process_checkout_step2(
    request: CheckoutStep2Request,
    step1_data: CheckoutStep1Request,
    db: Session = Depends(get_db)
):
    """
    Paso 2: Validar información de facturación y configurar pago
    - Validar campos de facturación
    - Validar método de pago
    - Crear PaymentIntent de Stripe
    """
    try:
        return await checkout_service.process_step2(request, step1_data)
    except Exception as e:
        logger.error(f"Error processing checkout step 2: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar paso 2: {str(e)}"
        )

@checkout_router.post("/step3", response_model=CheckoutStep3Response)
async def process_checkout_step3(
    request: CheckoutStep3Request,
    step1_data: CheckoutStep1Request,
    step2_data: CheckoutStep2Request,
    db: Session = Depends(get_db)
):
    """
    Paso 3: Crear orden final
    - Crear orden en WooCommerce
    - Configurar tracking
    - Retornar información de la orden
    """
    try:
        return await checkout_service.process_step3(request, step1_data, step2_data)
    except Exception as e:
        logger.error(f"Error processing checkout step 3: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar paso 3: {str(e)}"
        )

# === CONFIRMACIÓN DE PAGO ===

@checkout_router.post("/confirm-payment/{order_id}", response_model=OrderResponse)
async def confirm_payment(
    order_id: int,
    payment_intent_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Confirmar pago de una orden
    - Verificar PaymentIntent en Stripe
    - Marcar orden como pagada en WooCommerce
    - Actualizar estado de la orden
    """
    try:
        return await checkout_service.confirm_payment(order_id, payment_intent_id)
    except Exception as e:
        logger.error(f"Error confirming payment for order {order_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al confirmar pago: {str(e)}"
        )

# === ENDPOINTS DE UTILIDAD ===

@checkout_router.get("/default-payment-method")
async def get_default_payment_method(db: Session = Depends(get_db)):
    """Obtener método de pago por defecto"""
    try:
        from features.ecommerce.validation_service import ValidationService
        validation_service = ValidationService()
        return {"payment_method": validation_service.get_default_payment_method()}
    except Exception as e:
        logger.error(f"Error getting default payment method: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener método de pago por defecto: {str(e)}"
        )

@checkout_router.get("/valid-zip-codes")
async def get_valid_zip_codes(db: Session = Depends(get_db)):
    """Obtener lista de códigos postales válidos"""
    try:
        from features.ecommerce.validation_service import ValidationService
        validation_service = ValidationService()
        return {"valid_zip_codes": validation_service.valid_zip_codes}
    except Exception as e:
        logger.error(f"Error getting valid zip codes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener códigos postales válidos: {str(e)}"
        )

@checkout_router.get("/delivery-config")
async def get_delivery_config(db: Session = Depends(get_db)):
    """Obtener configuración de entregas"""
    try:
        from features.ecommerce.validation_service import ValidationService
        validation_service = ValidationService()
        return {
            "cutoff_time": validation_service.cutoff_time,
            "delivery_days": validation_service.delivery_days,
            "default_delivery_date": validation_service.calculate_delivery_date()[0]
        }
    except Exception as e:
        logger.error(f"Error getting delivery config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener configuración de entregas: {str(e)}"
        )

# === ENDPOINT DE CHECKOUT COMPLETO (OPCIONAL) ===

@checkout_router.post("/complete-checkout", response_model=CheckoutStep3Response)
async def complete_checkout(
    step1_data: CheckoutStep1Request,
    step2_data: CheckoutStep2Request,
    step3_data: CheckoutStep3Request,
    db: Session = Depends(get_db)
):
    """
    Procesar checkout completo en una sola llamada
    Útil para casos donde se quiere hacer todo de una vez
    """
    try:
        # Validar paso 1
        step1_response = await checkout_service.process_step1(step1_data)
        if not step1_response.is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error en paso 1: {', '.join(step1_response.errors)}"
            )
        
        # Validar paso 2
        step2_response = await checkout_service.process_step2(step2_data, step1_data)
        if not step2_response.is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error en paso 2: {', '.join(step2_response.errors)}"
            )
        
        # Procesar paso 3
        return await checkout_service.process_step3(step3_data, step1_data, step2_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing checkout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al completar checkout: {str(e)}"
        )

# === TRACKING Y HISTORIAL ===

@checkout_router.get("/track-order/{order_number}")
async def track_order(
    order_number: str,
    db: Session = Depends(get_db)
):
    """
    Tracking de orden solo con número de orden
    
    - Busca la orden por número
    - Obtiene información de tracking desde WooCommerce
    - NO requiere autenticación
    """
    try:
        # Buscar orden por número
        order = db.query(Order).filter(Order.id == order_number).first()
        
        if not order:
            return {
                "found": False,
                "message": "Orden no encontrada",
                "order_number": order_number
            }
        
        # Obtener tracking desde WooCommerce
        tracking_info = None
        try:
            tracking_info = await checkout_service.woo_proxy.get_tracking_info(order.woocommerce_order_id)
        except Exception as e:
            logger.warning(f"Could not get tracking info for order {order.woocommerce_order_id}: {str(e)}")
            tracking_info = {
                "status": "No tracking information available",
                "carrier": None,
                "tracking_number": None,
                "estimated_delivery": None
            }
        
        return {
            "found": True,
            "order": {
                "id": order.id,
                "woocommerce_id": order.woocommerce_order_id,
                "status": order.status,
                "payment_status": order.payment_status,
                "total": order.total,
                "customer_email": order.customer_email,
                "customer_name": order.customer_name,
                "created_at": order.created_at,
                "updated_at": order.updated_at
            },
            "tracking": tracking_info
        }
        
    except Exception as e:
        logger.error(f"Error tracking order {order_number}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al buscar orden: {str(e)}"
        )

@checkout_router.get("/customer-orders/{email}")
async def get_customer_orders(
    email: str,
    db: Session = Depends(get_db)
):
    """
    Obtener historial de compras por email
    
    - Busca todas las órdenes del email
    - Ordena por fecha más reciente
    - NO requiere autenticación
    """
    try:
        # Buscar todas las órdenes del email
        orders = db.query(Order).filter(
            Order.customer_email == email
        ).order_by(Order.created_at.desc()).all()
        
        if not orders:
            return {
                "found": False,
                "message": "No se encontraron órdenes para este email",
                "customer_email": email,
                "total_orders": 0,
                "orders": []
            }
        
        # Preparar datos de órdenes
        orders_data = []
        for order in orders:
            orders_data.append({
                "id": order.id,
                "woocommerce_id": order.woocommerce_order_id,
                "status": order.status,
                "payment_status": order.payment_status,
                "total": order.total,
                "customer_name": order.customer_name,
                "created_at": order.created_at,
                "updated_at": order.updated_at,
                "shipping_address": order.shipping_address,
                "billing_address": order.billing_address
            })
        
        return {
            "found": True,
            "customer_email": email,
            "total_orders": len(orders),
            "orders": orders_data
        }
        
    except Exception as e:
        logger.error(f"Error getting customer orders for {email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al buscar órdenes: {str(e)}"
        )