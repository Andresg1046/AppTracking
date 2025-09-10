"""
Servicio Proxy para WooCommerce - Solo interfaz, sin datos locales
"""
import httpx
import os
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from features.ecommerce.schemas import (
    ProductResponse, ProductVariation, ProductImage, OrderResponse, TrackingInfo, 
    OrderCreate, PaymentConfirm, TrackingUpdate
)
import logging

logger = logging.getLogger(__name__)

class WooCommerceProxy:
    """Proxy directo a WooCommerce - Sin datos locales"""
    
    def __init__(self):
        self.base_url = os.getenv("WC_BASE_URL", "https://your-domain.com/wp-json/wc/v3")
        self.consumer_key = os.getenv("WC_CONSUMER_KEY")
        self.consumer_secret = os.getenv("WC_CONSUMER_SECRET")
        
        if not self.consumer_key or not self.consumer_secret:
            raise ValueError("WooCommerce credentials not configured")
        
        self.auth = (self.consumer_key, self.consumer_secret)
        self.timeout = 10.0  # Reducir timeout de 30s a 10s
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Realizar petición HTTP a WooCommerce API"""
        url = f"{self.base_url}{endpoint}"
        
        async with httpx.AsyncClient(timeout=self.timeout, auth=self.auth) as client:
            try:
                response = await client.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"WooCommerce API error: {e.response.status_code} - {e.response.text}")
                raise Exception(f"WooCommerce API error: {e.response.text}")
            except Exception as e:
                logger.error(f"Error connecting to WooCommerce: {str(e)}")
                raise Exception(f"Error connecting to WooCommerce: {str(e)}")
    
    # === PRODUCTOS ===
    async def get_products(
        self, 
        page: int = 1, 
        per_page: int = 20, 
        search: Optional[str] = None,
        category: Optional[int] = None,
        featured: Optional[bool] = None,
        on_sale: Optional[bool] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        stock_status: Optional[str] = None
    ) -> tuple[List[ProductResponse], int]:
        """Obtener lista de productos directamente de WooCommerce"""
        params = {
            "page": page,
            "per_page": min(per_page, 100),
            "status": "publish"
        }
        
        if search:
            params["search"] = search
        if category:
            params["category"] = category
        if featured is not None:
            params["featured"] = featured
        if on_sale is not None:
            params["on_sale"] = on_sale
        if min_price is not None:
            params["min_price"] = min_price
        if max_price is not None:
            params["max_price"] = max_price
        if stock_status:
            params["stock_status"] = stock_status
        
        # Optimización: Solo obtener campos necesarios para el listado
        params["_fields"] = "id,name,slug,price,regular_price,sale_price,on_sale,stock_status,stock_quantity,images,categories,short_description,sku,type"
        
        response = await self._make_request("GET", "/products", params=params)
        
        # Transformar productos para móvil
        products = []
        for product_data in response:
            product = ProductResponse(
                id=product_data["id"],
                name=product_data["name"],
                slug=product_data["slug"],
                price=product_data["price"],
                regular_price=product_data["regular_price"],
                sale_price=product_data.get("sale_price"),
                on_sale=product_data["on_sale"],
                stock_status=product_data["stock_status"],
                stock_quantity=product_data.get("stock_quantity"),
                images=product_data.get("images", []),
                categories=product_data.get("categories", []),
                short_description=product_data.get("short_description", ""),
                sku=product_data.get("sku", ""),
                type=product_data.get("type", "simple"),
                variations=None  # No cargar variaciones en el listado
            )
            products.append(product)
        
        return products, len(products)
    
    async def _get_product_variations(self, product_id: int) -> List[ProductVariation]:
        """Obtener variaciones de un producto variable con todas las imágenes"""
        try:
            # Optimización: Hacer ambas llamadas en paralelo
            import asyncio
            
            # Llamadas paralelas para reducir tiempo
            product_task = self._make_request("GET", f"/products/{product_id}", params={"_fields": "images"})
            variations_task = self._make_request("GET", f"/products/{product_id}/variations", params={"_fields": "id,sku,price,regular_price,sale_price,on_sale,stock_status,stock_quantity,attributes,image"})
            
            # Esperar ambas respuestas
            product_response, variations_response = await asyncio.gather(product_task, variations_task)
            
            all_product_images = product_response.get("images", [])
            variations = []
            
            for variation_data in variations_response:
                # Obtener imagen específica de la variación si existe
                variation_image = None
                if variation_data.get("image"):
                    variation_image = ProductImage(
                        id=variation_data["image"]["id"],
                        src=variation_data["image"]["src"],
                        name=variation_data["image"]["name"],
                        alt=variation_data["image"]["alt"]
                    )
                
                # Crear lista de todas las imágenes disponibles para esta variación
                all_images = []
                
                # Agregar imagen específica de la variación si existe
                if variation_image:
                    all_images.append(variation_image)
                
                # Agregar todas las imágenes del producto padre
                for img_data in all_product_images:
                    img = ProductImage(
                        id=img_data["id"],
                        src=img_data["src"],
                        name=img_data["name"],
                        alt=img_data["alt"]
                    )
                    # Evitar duplicados
                    if not any(existing_img.id == img.id for existing_img in all_images):
                        all_images.append(img)
                
                variation = ProductVariation(
                    id=variation_data["id"],
                    sku=variation_data.get("sku", ""),
                    price=variation_data["price"],
                    regular_price=variation_data["regular_price"],
                    sale_price=variation_data.get("sale_price"),
                    on_sale=variation_data["on_sale"],
                    stock_status=variation_data["stock_status"],
                    stock_quantity=variation_data.get("stock_quantity"),
                    attributes=variation_data.get("attributes", []),
                    image=variation_image,  # Imagen principal de la variación
                    all_images=all_images    # Todas las imágenes disponibles
                )
                variations.append(variation)
            
            return variations
        except Exception as e:
            logger.error(f"Error getting variations for product {product_id}: {str(e)}")
            return []
    
    async def get_product(self, product_id: int) -> ProductResponse:
        """Obtener un producto específico de WooCommerce"""
        response = await self._make_request("GET", f"/products/{product_id}")
        
        # Obtener variaciones si es un producto variable
        variations = None
        if response.get("type") == "variable" and response.get("variations"):
            variations = await self._get_product_variations(product_id)
        
        return ProductResponse(
            id=response["id"],
            name=response["name"],
            slug=response["slug"],
            price=response["price"],
            regular_price=response["regular_price"],
            sale_price=response.get("sale_price"),
            on_sale=response["on_sale"],
            stock_status=response["stock_status"],
            stock_quantity=response.get("stock_quantity"),
            images=response.get("images", []),
            categories=response.get("categories", []),
            short_description=response.get("short_description", ""),
            sku=response.get("sku", ""),
            type=response.get("type", "simple"),
            variations=variations
        )
    
    # === CARRITO (Solo para mostrar, no persistir) ===
    async def calculate_cart_totals(self, cart_items: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calcular totales del carrito usando WooCommerce"""
        try:
            # Crear una orden temporal en WooCommerce para obtener los cálculos reales
            temp_order_data = {
                "payment_method": "temp",
                "payment_method_title": "Temporary",
                "set_paid": False,
                "billing": {
                    "first_name": "Temp",
                    "last_name": "User",
                    "company": "",
                    "address_1": "123 Temp St",
                    "address_2": "",
                    "city": "Temp City",
                    "state": "Temp State",
                    "postcode": "12345",
                    "country": "US",
                    "email": "temp@example.com",
                    "phone": "5551234567"
                },
                "shipping": {
                    "first_name": "Temp",
                    "last_name": "User",
                    "company": "",
                    "address_1": "123 Temp St",
                    "address_2": "",
                    "city": "Temp City",
                    "state": "Temp State",
                    "postcode": "12345",
                    "country": "US"
                },
                "line_items": cart_items,
                "meta_data": [
                    {
                        "key": "_temp_calculation",
                        "value": "true"
                    }
                ]
            }
            
            # Crear orden temporal en WooCommerce
            response = await self._make_request("POST", "/orders", json=temp_order_data)
            
            # Extraer los totales calculados por WooCommerce
            subtotal = float(response.get("total", 0)) - float(response.get("shipping_total", 0)) - float(response.get("total_tax", 0))
            tax_total = float(response.get("total_tax", 0))
            shipping_total = float(response.get("shipping_total", 0))
            total = float(response.get("total", 0))
            
            # Eliminar la orden temporal
            try:
                await self._make_request("DELETE", f"/orders/{response['id']}")
            except:
                pass  # Si no se puede eliminar, no es crítico
            
            return {
                "subtotal": subtotal,
                "tax_total": tax_total,
                "shipping_total": shipping_total,
                "total": total
            }
            
        except Exception as e:
            logger.error(f"Error calculating cart totals with WooCommerce: {str(e)}")
            # Fallback a cálculo simple si WooCommerce falla
            subtotal = 0.0
            for item in cart_items:
                subtotal += float(item["price"]) * item["quantity"]
            
            return {
                "subtotal": subtotal,
                "tax_total": 0.0,
                "shipping_total": 0.0,
                "total": subtotal
            }
    
    # === ÓRDENES ===
    async def create_order(self, order_data: OrderCreate) -> OrderResponse:
        """Crear orden directamente en WooCommerce con TODOS los campos"""
        
        # Meta data completa
        meta_data = []
        
        # Agregar campos de delivery
        if order_data.delivery_date:
            meta_data.append({
                "key": "_delivery_date",
                "value": order_data.delivery_date
            })
        
        if order_data.message_card:
            meta_data.append({
                "key": "_message_card",
                "value": order_data.message_card
            })
        
        if order_data.delivery_instructions:
            meta_data.append({
                "key": "_delivery_instructions",
                "value": order_data.delivery_instructions
            })
        
        if order_data.store_pickup:
            meta_data.append({
                "key": "_store_pickup",
                "value": "yes"
            })
        
        if order_data.location_type:
            meta_data.append({
                "key": "_location_type",
                "value": order_data.location_type
            })
        
        # Agregar meta data existente si hay
        if order_data.meta_data:
            meta_data.extend(order_data.meta_data)
        
        # Preparar datos para WooCommerce
        wc_order_data = {
            "payment_method": order_data.payment_method,
            "payment_method_title": order_data.payment_method_title,
            "set_paid": order_data.set_paid,
            "billing": order_data.billing.dict(),
            "shipping": order_data.shipping.dict() if order_data.shipping else order_data.billing.dict(),
            "line_items": order_data.line_items,
            "shipping_lines": order_data.shipping_lines or [],
            "coupon_lines": order_data.coupon_lines or [],
            "meta_data": meta_data
        }
        
        response = await self._make_request("POST", "/orders", json=wc_order_data)
        
        # Obtener tracking info si está disponible
        tracking_info = await self._get_tracking_info(response["id"])
        
        return OrderResponse(
            id=response["id"],
            status=response["status"],
            currency=response["currency"],
            total=response["total"],
            payment_method=response["payment_method"],
            payment_method_title=response["payment_method_title"],
            transaction_id=response.get("transaction_id"),
            date_created=response["date_created"],
            date_paid=response.get("date_paid"),
            billing=response["billing"],
            shipping=response["shipping"],
            line_items=response["line_items"],
            tracking_info=tracking_info
        )
    
    async def get_order(self, order_id: int) -> OrderResponse:
        """Obtener orden específica de WooCommerce"""
        response = await self._make_request("GET", f"/orders/{order_id}")
        
        # Obtener tracking info
        tracking_info = await self._get_tracking_info(order_id)
        
        return OrderResponse(
            id=response["id"],
            status=response["status"],
            currency=response["currency"],
            total=response["total"],
            payment_method=response["payment_method"],
            payment_method_title=response["payment_method_title"],
            transaction_id=response.get("transaction_id"),
            date_created=response["date_created"],
            date_paid=response.get("date_paid"),
            billing=response["billing"],
            shipping=response["shipping"],
            line_items=response["line_items"],
            tracking_info=tracking_info
        )
    
    async def get_customer_orders(
        self, 
        customer_id: Optional[int] = None,
        email: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> tuple[List[OrderResponse], int]:
        """Obtener órdenes de un cliente desde WooCommerce"""
        params = {
            "page": page,
            "per_page": min(per_page, 100)
        }
        
        if customer_id:
            params["customer"] = customer_id
        elif email:
            params["search"] = email
        
        response = await self._make_request("GET", "/orders", params=params)
        
        orders = []
        for order_data in response:
            # Obtener tracking info para cada orden
            tracking_info = await self._get_tracking_info(order_data["id"])
            
            order = OrderResponse(
                id=order_data["id"],
                status=order_data["status"],
                currency=order_data["currency"],
                total=order_data["total"],
                payment_method=order_data["payment_method"],
                payment_method_title=order_data["payment_method_title"],
                transaction_id=order_data.get("transaction_id"),
                date_created=order_data["date_created"],
                date_paid=order_data.get("date_paid"),
                billing=order_data["billing"],
                shipping=order_data["shipping"],
                line_items=order_data["line_items"],
                tracking_info=tracking_info
            )
            orders.append(order)
        
        return orders, len(orders)
    
    async def confirm_payment(self, order_id: int, payment_data: PaymentConfirm) -> OrderResponse:
        """Confirmar pago de una orden en WooCommerce"""
        update_data = {
            "status": payment_data.status,
            "set_paid": True,
            "transaction_id": payment_data.transaction_id,
        }
        
        # Agregar fecha de pago si se proporciona
        if payment_data.date_paid:
            update_data["date_paid"] = payment_data.date_paid.isoformat()
        
        # Agregar meta_data si se proporciona
        if payment_data.meta_data:
            update_data["meta_data"] = payment_data.meta_data
        
        # Agregar información de método de pago
        if payment_data.payment_method:
            update_data["payment_method"] = payment_data.payment_method
        if payment_data.payment_method_title:
            update_data["payment_method_title"] = payment_data.payment_method_title
        
        response = await self._make_request("PUT", f"/orders/{order_id}", json=update_data)
        
        # Obtener tracking info actualizado
        tracking_info = await self._get_tracking_info(order_id)
        
        return OrderResponse(
            id=response["id"],
            status=response["status"],
            currency=response["currency"],
            total=response["total"],
            payment_method=response["payment_method"],
            payment_method_title=response["payment_method_title"],
            transaction_id=response.get("transaction_id"),
            date_created=response["date_created"],
            date_paid=response.get("date_paid"),
            billing=response["billing"],
            shipping=response["shipping"],
            line_items=response["line_items"],
            tracking_info=tracking_info
        )
    
    # === TRACKING ===
    async def _get_tracking_info(self, order_id: int) -> Optional[TrackingInfo]:
        """Obtener información de tracking de una orden"""
        try:
            response = await self._make_request("GET", f"/orders/{order_id}/tracking")
            return TrackingInfo(**response)
        except:
            # Si no hay tracking info disponible, intentar obtener de meta_data
            try:
                order_response = await self._make_request("GET", f"/orders/{order_id}")
                meta_data = order_response.get("meta_data", [])
                
                tracking_data = {}
                for meta in meta_data:
                    key = meta.get("key", "")
                    value = meta.get("value", "")
                    
                    if key == "_tracking_carrier":
                        tracking_data["carrier"] = value
                    elif key == "_tracking_number":
                        tracking_data["number"] = value
                    elif key == "_tracking_url":
                        tracking_data["url"] = value
                    elif key == "_tracking_status":
                        tracking_data["status"] = value
                    elif key == "_estimated_delivery":
                        tracking_data["estimated_delivery"] = value
                
                if tracking_data:
                    return TrackingInfo(**tracking_data)
            except:
                pass
            
            return None
    
    async def update_tracking(self, order_id: int, tracking_data: TrackingUpdate) -> TrackingInfo:
        """Actualizar información de tracking en WooCommerce"""
        update_data = {
            "carrier": tracking_data.carrier,
            "number": tracking_data.number,
            "url": tracking_data.url,
            "status": tracking_data.status,
            "estimated_delivery": tracking_data.estimated_delivery.isoformat() if tracking_data.estimated_delivery else None
        }
        
        response = await self._make_request("POST", f"/orders/{order_id}/tracking", json=update_data)
        return TrackingInfo(**response["tracking_info"])
    
    # === CLIENTES ===
    async def get_customer(self, customer_id: int) -> Dict[str, Any]:
        """Obtener información de un cliente desde WooCommerce"""
        return await self._make_request("GET", f"/customers/{customer_id}")
    
    async def create_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crear un nuevo cliente en WooCommerce"""
        return await self._make_request("POST", "/customers", json=customer_data)
    
    # === CUPONES ===
    async def validate_coupon(self, coupon_code: str) -> Dict[str, Any]:
        """Validar cupón en WooCommerce"""
        try:
            response = await self._make_request("GET", f"/coupons/{coupon_code}")
            return {
                "valid": True,
                "discount_type": response.get("discount_type"),
                "amount": response.get("amount"),
                "description": response.get("description")
            }
        except:
            return {"valid": False, "message": "Cupón no válido"}
    
    # === CATEGORÍAS ===
    async def get_categories(self) -> List[Dict[str, Any]]:
        """Obtener categorías de productos desde WooCommerce"""
        response = await self._make_request("GET", "/products/categories")
        return response
