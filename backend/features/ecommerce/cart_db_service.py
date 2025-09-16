"""
Servicio de Carrito con Base de Datos
"""
import os
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
import logging

from core.database import get_db
from features.ecommerce.models import Cart, CartItem
from features.ecommerce.woocommerce_proxy import WooCommerceProxy

logger = logging.getLogger(__name__)

class CartDatabaseService:
    """
    Servicio de carrito que persiste datos en la base de datos
    
    - Cada sesión tiene su propio carrito
    - Los datos persisten entre reinicios del servidor
    - Al hacer checkout, se envía todo a WooCommerce
    """
    
    def __init__(self):
        self.woocommerce = WooCommerceProxy()
    
    async def _get_or_create_cart(self, db: Session, session_id: str) -> Cart:
        """Obtener o crear carrito para una sesión"""
        cart = db.query(Cart).filter(
            and_(
                Cart.session_id == session_id,
                Cart.is_active == True
            )
        ).first()
        
        if not cart:
            cart = Cart(session_id=session_id, user_id=0)  # user_id=0 para usuarios invitados
            db.add(cart)
            db.commit()
            db.refresh(cart)
        
        return cart
    
    async def _get_product_data(self, product_id: int) -> Dict[str, Any]:
        """Obtener datos del producto desde WooCommerce"""
        try:
            product_data = await self.woocommerce.get_product(product_id)
            return product_data
        except Exception as e:
            logger.error(f"Error getting product {product_id}: {str(e)}")
            raise Exception(f"Error getting product {product_id}: {str(e)}")
    
    async def _get_variation_data(self, variation_id: int) -> Dict[str, Any]:
        """Obtener datos específicos de una variación desde WooCommerce"""
        try:
            variation_data = await self.woocommerce._make_request("GET", f"/products/{variation_id}")
            return variation_data
        except Exception as e:
            logger.error(f"Error getting variation {variation_id}: {str(e)}")
            raise Exception(f"Error getting variation {variation_id}: {str(e)}")
    
    async def get_cart(self, session_id: str, db: Session) -> Dict[str, Any]:
        """
        Obtener carrito desde la base de datos
        """
        try:
            cart = await self._get_or_create_cart(db, session_id)
            logger.info(f"Cart found: ID={cart.id}, Session={cart.session_id}")
            
            # Obtener items del carrito explícitamente
            cart_items = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()
            logger.info(f"Found {len(cart_items)} items in cart {cart.id}")
            
            # Calcular totales
            total_items = len(cart_items)
            total_price = sum(item.line_total for item in cart_items)
            
            # Convertir items a formato JSON
            items_json = []
            for item in cart_items:
                item_data = {
                    "key": f"cart_item_{item.product_id}_{item.id}",
                    "id": item.product_id,
                    "type": "variation" if item.variation_id else "simple",
                    "quantity": item.quantity,
                    "quantity_limits": {
                        "minimum": 1,
                        "maximum": 999,
                        "multiple_of": 1,
                        "editable": True
                    },
                    "name": item.product_name,
                    "short_description": "",
                    "description": "",
                    "sku": item.product_sku or "",
                    "low_stock_remaining": None,
                    "backorders_allowed": False,
                    "show_backorder_badge": False,
                    "sold_individually": False,
                    "permalink": f"https://flowersfreehold.com/shop/product-{item.product_id}/",
                    "images": [
                        {
                            "id": 1,
                            "src": item.product_image_url or "",
                            "thumbnail": item.product_image_url or "",
                            "srcset": "",
                            "sizes": "",
                            "name": item.product_name,
                            "alt": item.product_name
                        }
                    ] if item.product_image_url else [],
                    "variation": item.variation_attributes or [],
                    "item_data": [],
                    "prices": {
                        "price": f"{item.product_price:.2f}",  # En dólares
                        "regular_price": f"{item.product_price:.2f}",
                        "sale_price": None,
                        "price_range": None,
                        "currency_code": "USD",
                        "currency_symbol": "$",
                        "currency_minor_unit": 2,
                        "currency_decimal_separator": ".",
                        "currency_thousand_separator": ",",
                        "currency_prefix": "$",
                        "currency_suffix": "",
                        "raw_prices": {
                            "precision": 6,
                            "price": f"{item.product_price:.2f}",
                            "regular_price": f"{item.product_price:.2f}",
                            "sale_price": None
                        }
                    },
                    "totals": {
                        "line_subtotal": f"{item.line_total:.2f}",  # En dólares
                        "line_subtotal_tax": "0.00",
                        "line_total": f"{item.line_total:.2f}",  # En dólares
                        "line_total_tax": "0.00",
                        "currency_code": "USD",
                        "currency_symbol": "$",
                        "currency_minor_unit": 2,
                        "currency_decimal_separator": ".",
                        "currency_thousand_separator": ",",
                        "currency_prefix": "$",
                        "currency_suffix": ""
                    },
                    "catalog_visibility": "visible",
                    "extensions": {}
                }
                items_json.append(item_data)
            
            return {
                "items": items_json,
                "coupons": [],
                "fees": [],
                "totals": {
                    "total_items": f"{total_price:.2f}",  # En dólares
                    "total_items_tax": "0.00",
                    "total_fees": "0.00",
                    "total_fees_tax": "0.00",
                    "total_discount": "0.00",
                    "total_discount_tax": "0.00",
                    "total_shipping": "0.00",
                    "total_shipping_tax": "0.00",
                    "total_price": f"{total_price:.2f}",  # En dólares
                    "total_tax": "0.00",
                    "tax_lines": [],
                    "currency_code": "USD",
                    "currency_symbol": "$",
                    "currency_minor_unit": 2,
                    "currency_decimal_separator": ".",
                    "currency_thousand_separator": ",",
                    "currency_prefix": "$",
                    "currency_suffix": ""
                },
                "shipping_address": None,
                "billing_address": None,
                "needs_payment": total_items > 0,
                "needs_shipping": total_items > 0,
                "payment_requirements": ["products"] if total_items > 0 else [],
                "has_calculated_shipping": False,
                "shipping_rates": [],
                "items_count": total_items,
                "items_weight": 0,
                "cross_sells": [],
                "errors": [],
                "payment_methods": ["stripe", "ppcp"],
                "extensions": {}
            }
            
        except Exception as e:
            logger.error(f"Error getting cart: {str(e)}")
            raise Exception(f"Error getting cart: {str(e)}")
    
    async def calculate_taxes(self, cart_data: Dict[str, Any], zip_code: str) -> Dict[str, Any]:
        """
        Calcular impuestos del carrito basado en ZIP code
        
        - Calcula impuestos sobre productos + envío
        - Usa la configuración real de WooCommerce (6.625% para NJ)
        - Retorna precios directamente en dólares
        """
        try:
            # Obtener totales actuales del carrito (ya en dólares)
            subtotal = float(cart_data["totals"]["total_items"])
            shipping = 10.0  # Costo fijo de envío (configurable)
            
            # Determinar tasa de impuesto basada en ZIP code
            tax_rate = self._get_tax_rate_by_zip(zip_code)
            
            # Calcular impuestos sobre (productos + envío)
            taxable_amount = subtotal + shipping
            tax_amount = taxable_amount * tax_rate
            total = taxable_amount + tax_amount
            
            # Crear tax_lines como en WooCommerce
            tax_lines = []
            if tax_amount > 0:
                tax_lines.append({
                    "id": 1,
                    "rate_code": f"US-NJ-{zip_code}-TAX-1",
                    "rate_id": 1,
                    "label": f"US-NJ Tax ({tax_rate*100:.3f}%)",
                    "compound": False,
                    "tax_total": f"{tax_amount:.2f}",  # En dólares
                    "shipping_tax_total": f"{shipping * tax_rate:.2f}",  # En dólares
                    "rate_percent": tax_rate * 100,
                    "meta_data": []
                })
            
            return {
                "subtotal": f"{subtotal:.2f}",  # En dólares
                "shipping": f"{shipping:.2f}",  # En dólares
                "tax": f"{tax_amount:.2f}",  # En dólares
                "total": f"{total:.2f}",  # En dólares
                "tax_rate": tax_rate,
                "tax_rate_percent": f"{tax_rate * 100:.3f}%",
                "tax_lines": tax_lines,
                "currency_code": "USD",
                "currency_symbol": "$",
                "breakdown": {
                    "products": subtotal,
                    "shipping": shipping,
                    "tax": tax_amount,
                    "total": total
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating taxes: {str(e)}")
            raise Exception(f"Error calculating taxes: {str(e)}")
    
    def _get_tax_rate_by_zip(self, zip_code: str) -> float:
        """
        Obtener tasa de impuesto basada en ZIP code
        
        Por ahora, todos los ZIP de NJ usan 6.625%
        """
        # Por simplicidad, asumimos que todos los ZIP de NJ usan la misma tasa
        # En el futuro se puede hacer más específico por ciudad/condado
        return 0.06625  # 6.625%
    
    async def add_to_cart(
        self, 
        session_id: str, 
        product_id: int, 
        quantity: int = 1, 
        variation_id: Optional[int] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Añadir producto al carrito en la base de datos
        """
        try:
            # Obtener datos del producto desde WooCommerce
            product_data = await self._get_product_data(product_id)
            
            # Si es una variación, obtener datos específicos de la variación
            variation_data = None
            variation_attributes = None
            if variation_id:
                variation_data = await self._get_variation_data(variation_id)
                # Extraer atributos de la variación
                if variation_data.get('attributes'):
                    variation_attributes = []
                    for attr in variation_data['attributes']:
                        if attr.get('option'):
                            variation_attributes.append({
                                'name': attr.get('name', ''),
                                'option': attr.get('option', '')
                            })
            
            # Obtener o crear carrito
            cart = await self._get_or_create_cart(db, session_id)
            
            # Verificar si el producto ya existe en el carrito
            existing_item = db.query(CartItem).filter(
                and_(
                    CartItem.cart_id == cart.id,
                    CartItem.product_id == product_id,
                    CartItem.variation_id == variation_id
                )
            ).first()
            
            if existing_item:
                # Actualizar cantidad existente
                existing_item.quantity += quantity
                existing_item.line_total = existing_item.quantity * existing_item.product_price
                existing_item.updated_at = db.query(Cart).filter(Cart.id == cart.id).first().updated_at
            else:
                # Determinar precio correcto: usar precio de variación si existe, sino precio del producto padre
                if variation_data and variation_data.get('price'):
                    product_price = float(variation_data['price'])
                    product_name = variation_data.get('name', product_data.name)
                    product_sku = variation_data.get('sku', product_data.sku)
                else:
                    product_price = float(product_data.price) if hasattr(product_data, 'price') and product_data.price else 0.0
                    product_name = product_data.name if hasattr(product_data, 'name') else "Product"
                    product_sku = product_data.sku if hasattr(product_data, 'sku') else None
                
                line_total = product_price * quantity
                
                # Obtener URL de imagen: priorizar imagen de variación, sino imagen del producto padre
                image_url = None
                if variation_data and variation_data.get('image') and variation_data['image'].get('src'):
                    image_url = variation_data['image']['src']
                elif hasattr(product_data, 'images') and product_data.images:
                    image_url = product_data.images[0].src if hasattr(product_data.images[0], 'src') else None
                
                cart_item = CartItem(
                    cart_id=cart.id,
                    product_id=product_id,
                    variation_id=variation_id,
                    quantity=quantity,
                    product_name=product_name,
                    product_sku=product_sku,
                    product_price=product_price,
                    product_image_url=image_url,
                    variation_attributes=variation_attributes,
                    line_total=line_total
                )
                
                db.add(cart_item)
            
            db.commit()
            
            # Retornar carrito actualizado
            return await self.get_cart(session_id, db)
            
        except Exception as e:
            logger.error(f"Error adding to cart: {str(e)}")
            raise Exception(f"Error adding to cart: {str(e)}")
    
    async def update_cart_item(
        self, 
        session_id: str, 
        cart_item_key: str, 
        quantity: int, 
        db: Session
    ) -> Dict[str, Any]:
        """
        Actualizar cantidad de item en el carrito
        """
        try:
            # Extraer ID del item desde la key
            item_id = int(cart_item_key.split("_")[-1])
            
            # Buscar el item
            cart_item = db.query(CartItem).filter(
                and_(
                    CartItem.id == item_id,
                    CartItem.cart.has(session_id=session_id)
                )
            ).first()
            
            if not cart_item:
                raise Exception(f"Cart item not found: {cart_item_key}")
            
            # Actualizar cantidad
            cart_item.quantity = quantity
            cart_item.line_total = cart_item.quantity * cart_item.product_price
            cart_item.updated_at = db.query(Cart).filter(Cart.id == cart_item.cart_id).first().updated_at
            
            db.commit()
            
            # Retornar carrito actualizado
            return await self.get_cart(session_id, db)
            
        except Exception as e:
            logger.error(f"Error updating cart item: {str(e)}")
            raise Exception(f"Error updating cart item: {str(e)}")
    
    async def remove_from_cart(
        self, 
        session_id: str, 
        cart_item_key: str, 
        db: Session
    ) -> Dict[str, Any]:
        """
        Eliminar item del carrito
        """
        try:
            # Extraer ID del item desde la key
            item_id = int(cart_item_key.split("_")[-1])
            
            # Buscar y eliminar el item
            cart_item = db.query(CartItem).filter(
                and_(
                    CartItem.id == item_id,
                    CartItem.cart.has(session_id=session_id)
                )
            ).first()
            
            if cart_item:
                db.delete(cart_item)
                db.commit()
            
            # Retornar carrito actualizado
            return await self.get_cart(session_id, db)
            
        except Exception as e:
            logger.error(f"Error removing from cart: {str(e)}")
            raise Exception(f"Error removing from cart: {str(e)}")
    
    async def clear_cart(self, session_id: str, db: Session) -> Dict[str, Any]:
        """
        Limpiar todo el carrito
        """
        try:
            # Buscar el carrito
            cart = db.query(Cart).filter(
                and_(
                    Cart.session_id == session_id,
                    Cart.is_active == True
                )
            ).first()
            
            if cart:
                # Eliminar todos los items
                db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
                db.commit()
            
            # Retornar carrito vacío
            return await self.get_cart(session_id, db)
            
        except Exception as e:
            logger.error(f"Error clearing cart: {str(e)}")
            raise Exception(f"Error clearing cart: {str(e)}")
    
    async def get_cart_totals(self, session_id: str, db: Session) -> Dict[str, Any]:
        """
        Obtener totales del carrito
        """
        # Retornar el carrito completo (que incluye totales)
        return await self.get_cart(session_id, db)
