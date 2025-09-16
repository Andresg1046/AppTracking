"""
Modelos de E-commerce para la Base de Datos
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from core.database import Base

class Cart(Base):
    """Modelo para el carrito de compras"""
    __tablename__ = "carts"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, nullable=True)  # Null para usuarios invitados
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relación con items del carrito
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")

class CartItem(Base):
    """Modelo para items individuales en el carrito"""
    __tablename__ = "cart_items"
    
    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    
    # Información del producto
    product_id = Column(Integer, nullable=False)
    variation_id = Column(Integer, nullable=True)
    quantity = Column(Integer, default=1)
    
    # Datos del producto (cached para evitar consultas repetidas)
    product_name = Column(String(500), nullable=False)
    product_sku = Column(String(100), nullable=True)
    product_price = Column(Float, nullable=False)
    product_image_url = Column(String(500), nullable=True)
    
    # Atributos de variación (si aplica)
    variation_attributes = Column(JSON, nullable=True)
    
    # Totales calculados
    line_total = Column(Float, nullable=False)  # quantity * product_price
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación con el carrito
    cart = relationship("Cart", back_populates="items")

class Order(Base):
    """Modelo para órdenes procesadas"""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    woocommerce_order_id = Column(Integer, nullable=True)  # ID de la orden en WooCommerce
    session_id = Column(String(255), nullable=True)
    user_id = Column(Integer, nullable=True)
    
    # Información del cliente
    customer_email = Column(String(255), nullable=False)
    customer_name = Column(String(255), nullable=False)
    customer_phone = Column(String(50), nullable=True)
    
    # Direcciones
    shipping_address = Column(JSON, nullable=True)
    billing_address = Column(JSON, nullable=True)
    
    # Totales
    subtotal = Column(Float, nullable=False)
    tax_total = Column(Float, default=0.0)
    shipping_total = Column(Float, default=0.0)
    total = Column(Float, nullable=False)
    
    # Estado
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    payment_status = Column(String(50), default="pending")  # pending, paid, failed, refunded
    
    # Información de pago
    payment_method = Column(String(100), nullable=True)
    payment_intent_id = Column(String(255), nullable=True)  # Stripe PaymentIntent ID
    
    # Metadatos
    notes = Column(Text, nullable=True)
    order_metadata = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación con items de la orden
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    
    # Relación con tracking de entrega
    delivery_tracking = relationship("DeliveryTracking", back_populates="order", uselist=False)

class OrderItem(Base):
    """Modelo para items individuales en una orden"""
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    
    # Información del producto
    product_id = Column(Integer, nullable=False)
    variation_id = Column(Integer, nullable=True)
    quantity = Column(Integer, nullable=False)
    
    # Datos del producto
    product_name = Column(String(500), nullable=False)
    product_sku = Column(String(100), nullable=True)
    product_price = Column(Float, nullable=False)
    
    # Atributos de variación
    variation_attributes = Column(JSON, nullable=True)
    
    # Totales
    line_total = Column(Float, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relación con la orden
    order = relationship("Order", back_populates="items")