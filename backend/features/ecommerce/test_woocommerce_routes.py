"""
Rutas de prueba para verificar conexión con WooCommerce
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
import httpx
import os
import uuid
from core.database import get_db
from features.ecommerce.woocommerce_cart_service import WooCommerceCartService
from features.ecommerce.cart_db_service import CartDatabaseService
import logging

logger = logging.getLogger(__name__)

test_woocommerce_router = APIRouter()

@test_woocommerce_router.get("/test-connection")
async def test_woocommerce_connection(db: Session = Depends(get_db)):
    """
    Probar conexión con WooCommerce
    """
    try:
        cart_service = WooCommerceCartService()
        
        # Probar obteniendo un producto
        test_product = await cart_service._make_request("GET", "/products", params={"per_page": 1})
        
        return {
            "status": "success",
            "message": "Conexión con WooCommerce exitosa",
            "test_data": {
                "products_found": len(test_product),
                "first_product": test_product[0] if test_product else None
            }
        }
        
    except Exception as e:
        logger.error(f"Error testing WooCommerce connection: {str(e)}")
        return {
            "status": "error",
            "message": f"Error conectando con WooCommerce: {str(e)}",
            "test_data": None
        }

@test_woocommerce_router.get("/test-product/{product_id}")
async def test_get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Probar obtención de producto específico
    """
    try:
        cart_service = WooCommerceCartService()
        
        # Obtener producto específico
        product = await cart_service._make_request("GET", f"/products/{product_id}")
        
        return {
            "status": "success",
            "message": f"Producto {product_id} obtenido exitosamente",
            "product": {
                "id": product["id"],
                "name": product["name"],
                "price": product["price"],
                "stock_status": product.get("stock_status"),
                "images": len(product.get("images", [])),
                "sku": product.get("sku")
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting product {product_id}: {str(e)}")
        return {
            "status": "error",
            "message": f"Error obteniendo producto {product_id}: {str(e)}",
            "product": None
        }

@test_woocommerce_router.post("/test-add-to-cart/{product_id}")
async def test_add_to_cart(product_id: int, quantity: int = 1, variation_id: Optional[int] = None, db: Session = Depends(get_db)):
    """
    Probar añadir producto al carrito (con o sin variación)
    """
    try:
        cart_service = WooCommerceCartService()
        
        # Añadir producto al carrito
        cart_data = await cart_service.add_to_cart(product_id, quantity, variation_id)
        
        return {
            "status": "success",
            "message": f"Producto {product_id} añadido al carrito exitosamente",
            "product_id": product_id,
            "variation_id": variation_id,
            "quantity": quantity,
            "cart_data": cart_data
        }
        
    except Exception as e:
        logger.error(f"Error adding product {product_id} to cart: {str(e)}")
        return {
            "status": "error",
            "message": f"Error añadiendo producto {product_id} al carrito: {str(e)}",
            "product_id": product_id,
            "variation_id": variation_id,
            "cart_data": None
        }

@test_woocommerce_router.post("/test-add-to-cart-db/{product_id}")
async def test_add_to_cart_db(
    product_id: int, 
    quantity: int = 1, 
    variation_id: Optional[int] = None, 
    session_id: str = Query(default_factory=lambda: str(uuid.uuid4())),
    db: Session = Depends(get_db)
):
    """
    Probar añadir producto al carrito usando el servicio de base de datos (con variaciones)
    """
    try:
        cart_service = CartDatabaseService()
        
        # Añadir producto al carrito usando base de datos
        cart_data = await cart_service.add_to_cart(
            session_id=session_id,
            product_id=product_id, 
            quantity=quantity, 
            variation_id=variation_id,
            db=db
        )
        
        return {
            "status": "success",
            "message": f"Producto {product_id} añadido al carrito DB exitosamente",
            "product_id": product_id,
            "variation_id": variation_id,
            "quantity": quantity,
            "session_id": session_id,
            "cart_data": cart_data
        }
        
    except Exception as e:
        logger.error(f"Error adding product {product_id} to cart DB: {str(e)}")
        return {
            "status": "error",
            "message": f"Error añadiendo producto {product_id} al carrito DB: {str(e)}",
            "product_id": product_id,
            "variation_id": variation_id,
            "session_id": session_id,
            "cart_data": None
        }

@test_woocommerce_router.get("/test-track-order/{order_number}")
async def test_track_order(
    order_number: str,
    db: Session = Depends(get_db)
):
    """
    Probar tracking de orden
    """
    try:
        from features.ecommerce.models import Order
        
        # Buscar orden por número
        order = db.query(Order).filter(Order.id == order_number).first()
        
        if not order:
            return {
                "status": "not_found",
                "message": f"Orden {order_number} no encontrada",
                "order_number": order_number
            }
        
        return {
            "status": "success",
            "message": f"Orden {order_number} encontrada",
            "order": {
                "id": order.id,
                "woocommerce_id": order.woocommerce_order_id,
                "status": order.status,
                "payment_status": order.payment_status,
                "total": order.total,
                "customer_email": order.customer_email,
                "customer_name": order.customer_name,
                "created_at": order.created_at
            }
        }
        
    except Exception as e:
        logger.error(f"Error tracking order {order_number}: {str(e)}")
        return {
            "status": "error",
            "message": f"Error al buscar orden {order_number}: {str(e)}",
            "order_number": order_number
        }

@test_woocommerce_router.get("/test-customer-orders/{email}")
async def test_customer_orders(
    email: str,
    db: Session = Depends(get_db)
):
    """
    Probar historial de compras por email
    """
    try:
        from features.ecommerce.models import Order
        
        # Buscar todas las órdenes del email
        orders = db.query(Order).filter(
            Order.customer_email == email
        ).order_by(Order.created_at.desc()).all()
        
        return {
            "status": "success",
            "message": f"Historial encontrado para {email}",
            "customer_email": email,
            "total_orders": len(orders),
            "orders": [
                {
                    "id": order.id,
                    "woocommerce_id": order.woocommerce_order_id,
                    "status": order.status,
                    "total": order.total,
                    "created_at": order.created_at
                }
                for order in orders
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting customer orders for {email}: {str(e)}")
        return {
            "status": "error",
            "message": f"Error al buscar órdenes para {email}: {str(e)}",
            "customer_email": email
        }

@test_woocommerce_router.get("/test-products")
async def test_get_products(db: Session = Depends(get_db)):
    """
    Obtener lista de productos para probar
    """
    try:
        cart_service = WooCommerceCartService()
        
        # Obtener productos usando REST API
        rest_api_url = os.getenv("WC_BASE_URL", "https://flowersfreehold.com/wp-json/wc/v3")
        if "/wc/store/v1" in rest_api_url:
            rest_api_url = rest_api_url.replace("/wc/store/v1", "/wc/v3")
        
        async with httpx.AsyncClient(timeout=10.0, auth=(os.getenv("WC_CONSUMER_KEY"), os.getenv("WC_CONSUMER_SECRET"))) as client:
            response = await client.get(f"{rest_api_url}/products", params={"per_page": 5})
            response.raise_for_status()
            products = response.json()
        
        return {
            "status": "success",
            "message": "Productos obtenidos exitosamente",
            "products": [
                {
                    "id": product["id"],
                    "name": product["name"],
                    "price": product["price"],
                    "type": product["type"],
                    "variations": product.get("variations", []),
                    "stock_status": product.get("stock_status")
                }
                for product in products
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting products: {str(e)}")
        return {
            "status": "error",
            "message": f"Error obteniendo productos: {str(e)}",
            "products": []
        }

@test_woocommerce_router.get("/test-store-api-routes")
async def test_store_api_routes(db: Session = Depends(get_db)):
    """
    Verificar qué endpoints están disponibles en la Store API
    """
    try:
        # URL de la Store API
        store_api_url = "https://flowersfreehold.com/wp-json/wc/store/v1"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Intentar obtener información de la API
            response = await client.get(f"{store_api_url}")
            if response.status_code == 200:
                api_info = response.json()
                return {
                    "status": "success",
                    "message": "Store API disponible",
                    "api_info": api_info
                }
            else:
                return {
                    "status": "error",
                    "message": f"Store API no disponible: {response.status_code}",
                    "response_text": response.text
                }
        
    except Exception as e:
        logger.error(f"Error checking Store API: {str(e)}")
        return {
            "status": "error",
            "message": f"Error verificando Store API: {str(e)}"
        }

@test_woocommerce_router.get("/test-cart-endpoints")
async def test_cart_endpoints(db: Session = Depends(get_db)):
    """
    Probar diferentes endpoints de carrito
    """
    try:
        cart_service = WooCommerceCartService()
        
        # Probar diferentes endpoints de carrito
        endpoints_to_test = [
            "/cart",
            "/cart/add-item", 
            "/cart/add",
            "/cart/items",
            "/cart/update-item",
            "/cart/remove-item"
        ]
        
        results = {}
        
        for endpoint in endpoints_to_test:
            try:
                response = await cart_service._make_request("GET", endpoint)
                results[endpoint] = {
                    "status": "success",
                    "method": "GET",
                    "response": response
                }
            except Exception as e:
                results[endpoint] = {
                    "status": "error",
                    "method": "GET", 
                    "error": str(e)
                }
        
        return {
            "status": "success",
            "message": "Endpoints de carrito probados",
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error testing cart endpoints: {str(e)}")
        return {
            "status": "error",
            "message": f"Error probando endpoints de carrito: {str(e)}"
        }

@test_woocommerce_router.get("/test-nonce")
async def test_nonce(db: Session = Depends(get_db)):
    """
    Probar obtención de nonce
    """
    try:
        cart_service = WooCommerceCartService()
        
        # Obtener nonce
        nonce = await cart_service._get_nonce()
        
        if nonce:
            return {
                "status": "success",
                "message": "Nonce obtenido exitosamente",
                "nonce": nonce,
                "nonce_length": len(nonce),
                "nonce_preview": nonce[:10] + "..." if len(nonce) > 10 else nonce
            }
        else:
            return {
                "status": "error",
                "message": "No se pudo obtener nonce"
            }
        
    except Exception as e:
        logger.error(f"Error testing nonce: {str(e)}")
        return {
            "status": "error",
            "message": f"Error probando nonce: {str(e)}"
        }

@test_woocommerce_router.get("/test-cart-headers")
async def test_cart_headers(db: Session = Depends(get_db)):
    """
    Probar headers de respuesta del carrito
    """
    try:
        import httpx
        import os
        
        # URL de la Store API
        store_api_url = "https://flowersfreehold.com/wp-json/wc/store/v1"
        
        async with httpx.AsyncClient(timeout=10.0, auth=(os.getenv("WC_CONSUMER_KEY"), os.getenv("WC_CONSUMER_SECRET"))) as client:
            response = await client.get(f"{store_api_url}/cart")
            response.raise_for_status()
            
            # Obtener todos los headers
            headers = dict(response.headers)
            
            return {
                "status": "success",
                "message": "Headers obtenidos exitosamente",
                "headers": headers,
                "nonce_headers": {
                    "X-WC-Store-API-Nonce": headers.get("X-WC-Store-API-Nonce"),
                    "Nonce": headers.get("Nonce"),
                    "X-WP-Nonce": headers.get("X-WP-Nonce")
                }
            }
        
    except Exception as e:
        logger.error(f"Error testing cart headers: {str(e)}")
        return {
            "status": "error",
            "message": f"Error probando headers del carrito: {str(e)}"
        }

@test_woocommerce_router.post("/test-add-with-nonce/{product_id}")
async def test_add_with_nonce(product_id: int, db: Session = Depends(get_db)):
    """
    Probar añadir producto con nonce
    """
    try:
        cart_service = WooCommerceCartService()
        
        # Intentar añadir producto
        result = await cart_service.add_to_cart(product_id, 1)
        
        return {
            "status": "success",
            "message": f"Producto {product_id} añadido exitosamente",
            "product_id": product_id,
            "cart_data": result
        }
        
    except Exception as e:
        logger.error(f"Error adding product {product_id}: {str(e)}")
        return {
            "status": "error",
            "message": f"Error añadiendo producto {product_id}: {str(e)}",
            "product_id": product_id,
            "cart_data": None
        }

@test_woocommerce_router.delete("/test-clear-cart")
async def test_clear_cart(db: Session = Depends(get_db)):
    """
    Limpiar carrito para pruebas
    """
    try:
        cart_service = WooCommerceCartService()
        
        # Limpiar carrito
        result = await cart_service.clear_cart()
        
        return {
            "status": "success",
            "message": "Carrito limpiado exitosamente",
            "cart_data": result
        }
        
    except Exception as e:
        logger.error(f"Error clearing cart: {str(e)}")
        return {
            "status": "error",
            "message": f"Error limpiando carrito: {str(e)}"
        }

@test_woocommerce_router.get("/test-cart-simple")
async def test_cart_simple(db: Session = Depends(get_db)):
    """
    Probar carrito simple
    """
    try:
        cart_service = WooCommerceCartService()
        
        # Obtener carrito
        result = await cart_service.get_cart()
        
        return {
            "status": "success",
            "message": "Carrito obtenido exitosamente",
            "cart_data": result
        }
        
    except Exception as e:
        logger.error(f"Error getting cart: {str(e)}")
        return {
            "status": "error",
            "message": f"Error obteniendo carrito: {str(e)}"
        }
