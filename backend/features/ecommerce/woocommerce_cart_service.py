"""
WooCommerce Cart Service - Simulación Simple para Testing
"""
import httpx
import os
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class WooCommerceCartService:
    """
    Servicio simple para simular carrito de WooCommerce
    
    - Simulación básica para testing
    - Compatible con la estructura esperada
    - Funciona como los otros endpoints
    - Mantiene estado del carrito en memoria
    """
    
    def __init__(self):
        self.base_url = os.getenv("WC_BASE_URL", "https://flowersfreehold.com/wp-json/wc/v3")
        self.consumer_key = os.getenv("WC_CONSUMER_KEY")
        self.consumer_secret = os.getenv("WC_CONSUMER_SECRET")
        
        if not self.consumer_key or not self.consumer_secret:
            raise ValueError("WooCommerce credentials not configured")
        
        self.auth = (self.consumer_key, self.consumer_secret)
        self.timeout = 10.0
        
        # Estado del carrito en memoria (para simulación)
        self._cart_items = []
        self._cart_total = 0.0

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

    async def get_cart(self) -> Dict[str, Any]:
        """
        Obtener carrito - Usa estado real en memoria
        """
        # Calcular total de items
        total_items = len(self._cart_items)
        total_price = sum(item.get("line_total", 0) for item in self._cart_items)
        
        return {
            "items": self._cart_items,
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

    async def add_to_cart(self, product_id: int, quantity: int = 1, variation_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Añadir producto al carrito - Simulación simple
        """
        try:
            # Obtener información del producto
            product_data = await self._make_request("GET", f"/products/{product_id}")
            
            # Simular añadir al carrito
            cart_item = {
                "key": f"cart_item_{product_id}_{quantity}",
                "id": product_id,
                "type": "variation" if variation_id else "simple",
                "quantity": quantity,
                "quantity_limits": {
                    "minimum": 1,
                    "maximum": 999,
                    "multiple_of": 1,
                    "editable": True
                },
                "name": product_data.get("name", "Product"),
                "short_description": product_data.get("short_description", ""),
                "description": product_data.get("description", ""),
                "sku": product_data.get("sku", ""),
                "low_stock_remaining": None,
                "backorders_allowed": product_data.get("backorders_allowed", False),
                "show_backorder_badge": False,
                "sold_individually": product_data.get("sold_individually", False),
                "permalink": product_data.get("permalink", ""),
                "images": product_data.get("images", []),
                "variation": [],
                "item_data": [],
                "prices": {
                    "price": f"{float(product_data.get('price', 0)):.2f}",  # En dólares
                    "regular_price": f"{float(product_data.get('regular_price', 0)):.2f}",
                    "sale_price": f"{float(product_data.get('sale_price', 0)):.2f}" if product_data.get("sale_price") else None,
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
                        "price": f"{float(product_data.get('price', 0)):.2f}",
                        "regular_price": f"{float(product_data.get('regular_price', 0)):.2f}",
                        "sale_price": f"{float(product_data.get('sale_price', 0)):.2f}" if product_data.get("sale_price") else None
                    }
                },
                "totals": {
                    "line_subtotal": f"{float(product_data.get('price', 0)) * quantity:.2f}",  # En dólares
                    "line_subtotal_tax": "0.00",
                    "line_total": f"{float(product_data.get('price', 0)) * quantity:.2f}",  # En dólares
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
            
            # Añadir el producto al carrito en memoria
            cart_item["line_total"] = float(product_data.get("price", 0)) * quantity
            self._cart_items.append(cart_item)
            
            # Retornar el carrito actualizado
            return await self.get_cart()
            
        except Exception as e:
            logger.error(f"Error adding to cart: {str(e)}")
            raise Exception(f"Error adding to cart: {str(e)}")

    async def update_cart_item(self, cart_item_key: str, quantity: int) -> Dict[str, Any]:
        """
        Actualizar cantidad en carrito - Usa estado real
        """
        # Buscar el item en el carrito
        for item in self._cart_items:
            if item.get("key") == cart_item_key:
                # Actualizar cantidad
                item["quantity"] = quantity
                # Recalcular total
                price_per_item = float(item["prices"]["price"])  # Ya en dólares
                item["line_total"] = price_per_item * quantity
                item["totals"]["line_total"] = f"{price_per_item * quantity:.2f}"  # En dólares
                break
        
        # Retornar carrito actualizado
        return await self.get_cart()

    async def remove_from_cart(self, cart_item_key: str) -> Dict[str, Any]:
        """
        Eliminar producto del carrito - Usa estado real
        """
        # Remover el item del carrito
        self._cart_items = [item for item in self._cart_items if item.get("key") != cart_item_key]
        
        # Retornar carrito actualizado
        return await self.get_cart()

    async def clear_cart(self) -> Dict[str, Any]:
        """
        Limpiar carrito - Usa estado real
        """
        # Limpiar todos los items del carrito
        self._cart_items = []
        
        # Retornar carrito vacío
        return await self.get_cart()

    async def get_cart_totals(self) -> Dict[str, Any]:
        """
        Obtener totales del carrito - Usa estado real
        """
        # Retornar el carrito completo (que incluye totales)
        return await self.get_cart()