"""
WooCommerce Cart Routes - Conectar App Móvil a Carrito Existente
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import uuid

from core.database import get_db
# No se requiere autenticación para el carrito (como WordPress)
from features.ecommerce.cart_db_service import CartDatabaseService
from features.ecommerce.schemas import (
    CartItemRequest,
    CartUpdateRequest,
    CartResponse,
    CartItem,
    CartTotalsResponse
)

logger = logging.getLogger(__name__)

# Router para carrito de WooCommerce
woocommerce_cart_router = APIRouter()

@woocommerce_cart_router.get("/cart")
async def get_woocommerce_cart(
    session_id: str = Query(default_factory=lambda: str(uuid.uuid4()), description="ID de sesión del carrito"),
    db: Session = Depends(get_db)
):
    """
    Obtener carrito desde la base de datos
    
    - Persiste en la base de datos
    - Cada sesión tiene su propio carrito
    - NO requiere autenticación (como WordPress)
    """
    try:
        cart_service = CartDatabaseService()
        
        # Obtener carrito desde la base de datos
        cart_data = await cart_service.get_cart(session_id, db)
        
        return cart_data
        
    except Exception as e:
        logger.error(f"Error getting cart: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener carrito: {str(e)}"
        )

@woocommerce_cart_router.post("/cart/add")
async def add_to_woocommerce_cart(
    request: CartItemRequest,
    db: Session = Depends(get_db)
):
    """
    Añadir producto al carrito en la base de datos
    
    - Persiste en la base de datos
    - Obtiene datos del producto desde WooCommerce
    - Cada sesión tiene su propio carrito
    - NO requiere autenticación (como WordPress)
    """
    try:
        cart_service = CartDatabaseService()
        
        # Añadir a carrito en la base de datos
        cart_data = await cart_service.add_to_cart(
            session_id=request.session_id,
            product_id=request.product_id,
            quantity=request.quantity,
            variation_id=request.variation_id,
            db=db
        )
        
        return cart_data
        
    except Exception as e:
        logger.error(f"Error adding to cart: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al añadir al carrito: {str(e)}"
        )

@woocommerce_cart_router.put("/cart/update")
async def update_woocommerce_cart_item(
    request: CartUpdateRequest,
    session_id: str = Query(..., description="ID de sesión del carrito"),
    db: Session = Depends(get_db)
):
    """
    Actualizar cantidad en carrito
    
    - Persiste en la base de datos
    - Actualiza cantidad del producto
    - NO requiere autenticación (como WordPress)
    """
    try:
        cart_service = CartDatabaseService()
        
        # Actualizar carrito en la base de datos
        cart_data = await cart_service.update_cart_item(
            session_id=session_id,
            cart_item_key=request.cart_item_key,
            quantity=request.quantity,
            db=db
        )
        
        return cart_data
        
    except Exception as e:
        logger.error(f"Error updating cart: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar carrito: {str(e)}"
        )

@woocommerce_cart_router.delete("/cart/remove/{cart_item_key}")
async def remove_from_woocommerce_cart(
    cart_item_key: str,
    session_id: str = Query(..., description="ID de sesión del carrito"),
    db: Session = Depends(get_db)
):
    """
    Eliminar producto del carrito
    
    - Persiste en la base de datos
    - Elimina producto específico
    - NO requiere autenticación (como WordPress)
    """
    try:
        cart_service = CartDatabaseService()
        
        # Eliminar de carrito en la base de datos
        cart_data = await cart_service.remove_from_cart(
            session_id=session_id,
            cart_item_key=cart_item_key,
            db=db
        )
        
        return cart_data
        
    except Exception as e:
        logger.error(f"Error removing from cart: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar del carrito: {str(e)}"
        )

@woocommerce_cart_router.delete("/cart/clear")
async def clear_woocommerce_cart(
    session_id: str = Query(..., description="ID de sesión del carrito"),
    db: Session = Depends(get_db)
):
    """
    Limpiar carrito
    
    - Persiste en la base de datos
    - Elimina todos los productos
    - NO requiere autenticación (como WordPress)
    """
    try:
        cart_service = CartDatabaseService()
        
        # Limpiar carrito en la base de datos
        cart_data = await cart_service.clear_cart(
            session_id=session_id,
            db=db
        )
        
        return cart_data
        
    except Exception as e:
        logger.error(f"Error clearing cart: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al limpiar carrito: {str(e)}"
        )

@woocommerce_cart_router.get("/cart/totals")
async def get_woocommerce_cart_totals(
    session_id: str = Query(..., description="ID de sesión del carrito"),
    db: Session = Depends(get_db)
):
    """
    Obtener totales del carrito
    
    - Persiste en la base de datos
    - Incluye totales calculados
    - NO requiere autenticación (como WordPress)
    """
    try:
        cart_service = CartDatabaseService()
        
        # Obtener totales desde la base de datos
        totals = await cart_service.get_cart_totals(
            session_id=session_id,
            db=db
        )
        
        return totals
        
    except Exception as e:
        logger.error(f"Error getting cart totals: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener totales: {str(e)}"
        )

@woocommerce_cart_router.post("/cart/calculate-taxes")
async def calculate_cart_taxes(
    session_id: str = Query(..., description="ID de sesión del carrito"),
    zip_code: str = Query(..., description="Código postal para calcular impuestos"),
    db: Session = Depends(get_db)
):
    """
    Calcular impuestos del carrito basado en ZIP code
    
    - Calcula impuestos sobre productos + envío
    - Usa la configuración real de WooCommerce
    - NO requiere autenticación (como WordPress)
    """
    try:
        cart_service = CartDatabaseService()
        
        # Obtener carrito actual
        cart = await cart_service.get_cart(session_id, db)
        
        # Calcular impuestos
        tax_calculation = await cart_service.calculate_taxes(cart, zip_code)
        
        return tax_calculation
        
    except Exception as e:
        logger.error(f"Error calculating cart taxes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al calcular impuestos: {str(e)}"
        )