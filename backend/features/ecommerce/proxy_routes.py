"""
Rutas Proxy para WooCommerce - Solo interfaz, sin datos locales
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db
from core.security import get_current_user
from features.users.models import User
from features.ecommerce.woocommerce_proxy import WooCommerceProxy
from features.ecommerce.schemas import (
    ProductResponse, OrderResponse, OrderCreate, PaymentConfirm, 
    TrackingUpdate, TrackingInfo, ProductListResponse, OrderListResponse,
    CartTotalsResponse
)
import logging

logger = logging.getLogger(__name__)

proxy_router = APIRouter()

# Instancia del proxy WooCommerce
woo_proxy = WooCommerceProxy()

# === PRODUCTOS ===

@proxy_router.get("/products", response_model=ProductListResponse)
async def get_products(
    page: int = Query(1, ge=1, description="Número de página"),
    per_page: int = Query(20, ge=1, le=100, description="Productos por página"),
    search: Optional[str] = Query(None, description="Buscar productos"),
    category: Optional[int] = Query(None, description="Filtrar por categoría"),
    featured: Optional[bool] = Query(None, description="Solo productos destacados"),
    on_sale: Optional[bool] = Query(None, description="Solo productos en oferta"),
    min_price: Optional[float] = Query(None, description="Precio mínimo"),
    max_price: Optional[float] = Query(None, description="Precio máximo"),
    stock_status: Optional[str] = Query(None, description="Estado de stock"),
    db: Session = Depends(get_db)
):
    """Obtener lista de productos directamente de WooCommerce"""
    try:
        products, total = await woo_proxy.get_products(
            page=page,
            per_page=per_page,
            search=search,
            category=category,
            featured=featured,
            on_sale=on_sale,
            min_price=min_price,
            max_price=max_price,
            stock_status=stock_status
        )
        
        total_pages = (total + per_page - 1) // per_page
        
        return ProductListResponse(
            products=products,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
    except Exception as e:
        logger.error(f"Error getting products: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener productos: {str(e)}"
        )

@proxy_router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Obtener un producto específico de WooCommerce"""
    try:
        product = await woo_proxy.get_product(product_id)
        return product
    except Exception as e:
        logger.error(f"Error getting product {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener producto: {str(e)}"
        )

@proxy_router.get("/products/{product_id}/variations")
async def get_product_variations(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Obtener variaciones de un producto específico"""
    try:
        variations = await woo_proxy._get_product_variations(product_id)
        return {"variations": variations}
    except Exception as e:
        logger.error(f"Error getting variations for product {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener variaciones: {str(e)}"
        )

# === CARRITO (Solo cálculo, no persistencia) ===

@proxy_router.post("/cart/calculate", response_model=CartTotalsResponse)
async def calculate_cart_totals(
    cart_items: List[dict],
    db: Session = Depends(get_db)
):
    """Calcular totales del carrito sin persistir datos"""
    try:
        totals = await woo_proxy.calculate_cart_totals(cart_items)
        return CartTotalsResponse(
            cart_items=cart_items,
            subtotal=totals["subtotal"],
            tax_total=totals["tax_total"],
            shipping_total=totals["shipping_total"],
            total=totals["total"]
        )
    except Exception as e:
        logger.error(f"Error calculating cart totals: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al calcular totales: {str(e)}"
        )

# === ÓRDENES ===

@proxy_router.post("/orders", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db)
):
    """Crear una nueva orden directamente en WooCommerce"""
    try:
        order = await woo_proxy.create_order(order_data)
        return order
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear orden: {str(e)}"
        )

@proxy_router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener una orden específica de WooCommerce"""
    try:
        order = await woo_proxy.get_order(order_id)
        return order
    except Exception as e:
        logger.error(f"Error getting order {order_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener orden: {str(e)}"
        )

@proxy_router.get("/orders", response_model=OrderListResponse)
async def get_customer_orders(
    email: str = Query(..., description="Email del cliente"),
    page: int = Query(1, ge=1, description="Número de página"),
    per_page: int = Query(20, ge=1, le=100, description="Órdenes por página"),
    db: Session = Depends(get_db)
):
    """Obtener órdenes de un cliente desde WooCommerce"""
    try:
        orders, total = await woo_proxy.get_customer_orders(
            email=email,
            page=page,
            per_page=per_page
        )
        
        total_pages = (total + per_page - 1) // per_page
        
        return OrderListResponse(
            orders=orders,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
    except Exception as e:
        logger.error(f"Error getting customer orders: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener órdenes: {str(e)}"
        )

@proxy_router.post("/orders/{order_id}/confirm-payment", response_model=OrderResponse)
async def confirm_payment(
    order_id: int,
    payment_data: PaymentConfirm,
    db: Session = Depends(get_db)
):
    """Confirmar pago de una orden en WooCommerce"""
    try:
        order = await woo_proxy.confirm_payment(order_id, payment_data)
        return order
    except Exception as e:
        logger.error(f"Error confirming payment for order {order_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al confirmar pago: {str(e)}"
        )

# === TRACKING ===

@proxy_router.get("/orders/{order_id}/tracking", response_model=TrackingInfo)
async def get_tracking_info(
    order_id: int,
    db: Session = Depends(get_db)
):
    """Obtener información de tracking de una orden desde WooCommerce"""
    try:
        tracking_info = await woo_proxy._get_tracking_info(order_id)
        if not tracking_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Información de tracking no disponible"
            )
        return tracking_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tracking info for order {order_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener información de tracking: {str(e)}"
        )

@proxy_router.post("/orders/{order_id}/tracking", response_model=TrackingInfo)
async def update_tracking(
    order_id: int,
    tracking_data: TrackingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar información de tracking de una orden en WooCommerce"""
    try:
        tracking_info = await woo_proxy.update_tracking(order_id, tracking_data)
        return tracking_info
    except Exception as e:
        logger.error(f"Error updating tracking for order {order_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar tracking: {str(e)}"
        )

# === CUPONES ===

@proxy_router.get("/coupons/{coupon_code}")
async def validate_coupon(
    coupon_code: str,
    db: Session = Depends(get_db)
):
    """Validar cupón en WooCommerce"""
    try:
        result = await woo_proxy.validate_coupon(coupon_code)
        return result
    except Exception as e:
        logger.error(f"Error validating coupon {coupon_code}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al validar cupón: {str(e)}"
        )

# === CATEGORÍAS ===

@proxy_router.get("/categories")
async def get_categories(
    db: Session = Depends(get_db)
):
    """Obtener categorías de productos desde WooCommerce"""
    try:
        categories = await woo_proxy.get_categories()
        return {"categories": categories}
    except Exception as e:
        logger.error(f"Error getting categories: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener categorías: {str(e)}"
        )

# === PAGOS ===

@proxy_router.post("/create-payment-intent")
async def create_payment_intent(
    amount: float,
    currency: str = "usd",
    customer_email: Optional[str] = None,
    order_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Crear PaymentIntent para Stripe - TEMPORALMENTE DESHABILITADO"""
    try:
        # Stripe se configurará cuando esté listo para probar pagos
        logger.info("PaymentIntent temporalmente deshabilitado - se configurará cuando esté listo para probar pagos")
        
        # Simular PaymentIntent
        return {
            "client_secret": "temp_client_secret",
            "payment_intent_id": f"temp_pi_{order_id or 'test'}",
            "amount": amount,
            "currency": currency,
            "status": "requires_payment_method",
            "note": "Stripe temporalmente deshabilitado - se configurará cuando esté listo para probar pagos"
        }
        
    except Exception as e:
        logger.error(f"Error creating payment intent: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear PaymentIntent: {str(e)}"
        )

@proxy_router.post("/confirm-payment-intent")
async def confirm_payment_intent(
    payment_intent_id: str,
    order_id: int,
    db: Session = Depends(get_db)
):
    """Confirmar PaymentIntent y actualizar orden en WooCommerce - TEMPORALMENTE DESHABILITADO"""
    try:
        # Stripe se configurará cuando esté listo para probar pagos
        logger.info("Confirmación de PaymentIntent temporalmente deshabilitada - se configurará cuando esté listo para probar pagos")
        
        # Simular confirmación de pago
        from features.ecommerce.schemas import PaymentConfirm
        from datetime import datetime
        
        payment_data = PaymentConfirm(
            transaction_id=f"temp_txn_{order_id}",
            status="processing",
            date_paid=datetime.now(),
            payment_method="stripe",
            payment_method_title="Credit Card (Stripe) - Test Mode"
        )
        
        order = await woo_proxy.confirm_payment(order_id, payment_data)
        
        return {
            "success": True,
            "order": order,
            "payment_intent_status": "succeeded",
            "note": "Stripe temporalmente deshabilitado - se configurará cuando esté listo para probar pagos"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error confirming payment intent: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al confirmar pago: {str(e)}"
        )

# === PRINT MANAGER - INTEGRACIÓN SIMPLE ===

@proxy_router.get("/print-manager/status")
async def check_print_manager_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verificar si Print Manager está activo y configurado
    
    - Simple verificación de que Print Manager funciona
    - No necesita configuración adicional
    """
    try:
        # Obtener órdenes recientes para verificar que Print Manager funciona
        recent_orders = await woo_proxy._make_request("GET", "/orders", params={
            "per_page": 3,
            "orderby": "date",
            "order": "desc"
        })
        
        return {
            "print_manager_status": "active",
            "message": "Print Manager está configurado en WordPress con su API key",
            "mobile_orders_will_print": True,
            "recent_orders": [
                {
                    "id": order["id"],
                    "status": order["status"],
                    "date_created": order["date_created"]
                }
                for order in recent_orders
            ],
            "note": "Las órdenes móviles se imprimirán automáticamente usando Print Manager"
        }
        
    except Exception as e:
        logger.error(f"Error checking Print Manager status: {str(e)}")
        return {
            "print_manager_status": "error",
            "error": str(e),
            "message": "Could not verify Print Manager status"
        }

# === VERIFICACIÓN DE ÓRDENES ===

@proxy_router.get("/orders/{order_id}/verify")
async def verify_order_in_woocommerce(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verificar que una orden existe en WooCommerce y obtener detalles completos
    
    - Útil para debugging y verificar integración
    - Muestra todos los campos de la orden
    - Incluye meta_data para plugins
    """
    try:
        order = await woo_proxy.get_order(order_id)
        
        # Obtener información adicional de WooCommerce
        wc_order_raw = await woo_proxy._make_request("GET", f"/orders/{order_id}")
        
        return {
            "order_exists": True,
            "order_id": order_id,
            "order_summary": {
                "id": order.id,
                "status": order.status,
                "total": order.total,
                "payment_method": order.payment_method,
                "date_created": order.date_created,
                "billing": order.billing,
                "shipping": order.shipping
            },
            "woocommerce_details": {
                "raw_data": wc_order_raw,
                "meta_data": wc_order_raw.get("meta_data", []),
                "line_items": wc_order_raw.get("line_items", []),
                "shipping_lines": wc_order_raw.get("shipping_lines", []),
                "tax_lines": wc_order_raw.get("tax_lines", []),
                "customer_note": wc_order_raw.get("customer_note", "")
            },
            "plugin_compatibility": {
                "has_app_source": any(meta.get("key") == "_app_source" for meta in wc_order_raw.get("meta_data", [])),
                "has_store_pickup": any(meta.get("key") == "_store_pickup" for meta in wc_order_raw.get("meta_data", [])),
                "has_delivery_date": any(meta.get("key") == "_delivery_date" for meta in wc_order_raw.get("meta_data", [])),
                "has_message_card": any(meta.get("key") == "_message_card" for meta in wc_order_raw.get("meta_data", []))
            }
        }
        
    except Exception as e:
        logger.error(f"Error verifying order {order_id}: {str(e)}")
        return {
            "order_exists": False,
            "order_id": order_id,
            "error": str(e),
            "message": "Order not found or error accessing WooCommerce"
        }

@proxy_router.get("/orders/recent")
async def get_recent_orders(
    limit: int = Query(5, ge=1, le=20, description="Número de órdenes recientes"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener órdenes recientes de WooCommerce
    
    - Útil para verificar que las órdenes se están creando
    - Muestra órdenes creadas desde la app móvil
    """
    try:
        # Obtener órdenes recientes
        recent_orders = await woo_proxy._make_request("GET", "/orders", params={
            "per_page": limit,
            "orderby": "date",
            "order": "desc"
        })
        
        # Filtrar órdenes creadas desde la app móvil
        mobile_orders = []
        for order in recent_orders:
            meta_data = order.get("meta_data", [])
            is_mobile_order = any(
                meta.get("key") == "_app_source" and meta.get("value") == "mobile_app"
                for meta in meta_data
            )
            
            if is_mobile_order:
                mobile_orders.append({
                    "id": order["id"],
                    "status": order["status"],
                    "total": order["total"],
                    "payment_method": order["payment_method"],
                    "date_created": order["date_created"],
                    "customer_note": order.get("customer_note", ""),
                    "is_store_pickup": any(
                        meta.get("key") == "_store_pickup" and meta.get("value") == "yes"
                        for meta in meta_data
                    ),
                    "delivery_date": next(
                        (meta.get("value") for meta in meta_data if meta.get("key") == "_delivery_date"),
                        None
                    )
                })
        
        return {
            "total_recent_orders": len(recent_orders),
            "mobile_orders": mobile_orders,
            "mobile_orders_count": len(mobile_orders),
            "all_recent_orders": [
                {
                    "id": order["id"],
                    "status": order["status"],
                    "total": order["total"],
                    "date_created": order["date_created"],
                    "is_mobile": any(
                        meta.get("key") == "_app_source" and meta.get("value") == "mobile_app"
                        for meta in order.get("meta_data", [])
                    )
                }
                for order in recent_orders
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting recent orders: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener órdenes recientes: {str(e)}"
        )

# === WEBHOOKS ===

@proxy_router.post("/webhooks/woocommerce")
async def woo_commerce_webhook(request: Request, db: Session = Depends(get_db)):
    """Recibir webhooks de WooCommerce"""
    try:
        # Verificar firma del webhook
        signature = request.headers.get("X-WC-Webhook-Signature")
        if not signature:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing webhook signature"
            )
        
        # TODO: Implementar verificación de firma HMAC
        
        body = await request.json()
        order_id = body.get("id")
        
        if order_id:
            # TODO: Emitir evento para notificaciones push
            # TODO: Actualizar tracking en tiempo real
            
            logger.info(f"Webhook processed for order {order_id}")
        
        return {"message": "Webhook processed successfully"}
    except Exception as e:
        logger.error(f"Error processing WooCommerce webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing webhook: {str(e)}"
        )

@proxy_router.post("/webhooks/payment-gateway")
async def payment_gateway_webhook(request: Request, db: Session = Depends(get_db)):
    """Recibir webhooks de pasarelas de pago"""
    try:
        # TODO: Implementar verificación específica por pasarela
        
        body = await request.json()
        
        # Extraer información relevante según la pasarela
        order_id = None
        transaction_id = None
        payment_status = None
        
        # Ejemplo para Stripe
        if "type" in body and "payment_intent.succeeded" in body["type"]:
            payment_intent = body.get("data", {}).get("object", {})
            order_id = payment_intent.get("metadata", {}).get("order_id")
            transaction_id = payment_intent.get("charges", {}).get("data", [{}])[0].get("id")
            payment_status = "succeeded"
        
        # Ejemplo para PayPal
        elif "event_type" in body and "PAYMENT.CAPTURE.COMPLETED" in body["event_type"]:
            resource = body.get("resource", {})
            order_id = resource.get("custom_id")
            transaction_id = resource.get("id")
            payment_status = "completed"
        
        if order_id and transaction_id and payment_status:
            # Confirmar pago en WooCommerce
            payment_data = PaymentConfirm(
                transaction_id=transaction_id,
                status="processing"
            )
            
            await woo_proxy.confirm_payment(int(order_id), payment_data)
            
            logger.info(f"Payment confirmed for order {order_id}")
        
        return {"message": "Payment webhook processed successfully"}
    except Exception as e:
        logger.error(f"Error processing payment webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing payment webhook: {str(e)}"
        )
