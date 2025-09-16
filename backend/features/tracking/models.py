"""
Modelos para el sistema de tracking en tiempo real
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

class Driver(Base):
    """Modelo para conductores - Extensión de User"""
    __tablename__ = "drivers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True, index=True)
    
    # Estado del conductor
    is_online = Column(Boolean, default=False, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
    is_delivering = Column(Boolean, default=False, nullable=False)
    
    # Ubicación actual
    current_location = Column(JSON, nullable=True)  # {"lat": 40.7128, "lng": -74.0060, "accuracy": 10}
    last_location_update = Column(DateTime, nullable=True)
    
    # Información específica del conductor
    driver_license = Column(String(50), nullable=True)
    phone = Column(String(20), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Configuración de tracking
    location_update_interval = Column(Integer, default=30)  # segundos
    auto_location_sharing = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relaciones
    user = relationship("User", back_populates="driver_profile")
    vehicle = relationship("Vehicle", back_populates="assigned_driver")
    deliveries = relationship("DeliveryTracking", back_populates="driver")
    location_updates = relationship("LocationUpdate", back_populates="driver")

class DeliveryTracking(Base):
    """Modelo para seguimiento de entregas"""
    __tablename__ = "delivery_tracking"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=False, index=True)
    
    # Estado de la entrega
    status = Column(String(50), default="assigned", nullable=False)  # assigned, started, in_progress, completed, failed
    priority = Column(String(20), default="normal", nullable=False)  # low, normal, high, urgent
    
    # Timestamps
    assigned_at = Column(DateTime, default=func.now(), nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Ubicación de entrega
    delivery_address = Column(JSON, nullable=True)  # Dirección completa
    delivery_coordinates = Column(JSON, nullable=True)  # {"lat": 40.7128, "lng": -74.0060}
    
    # Estimaciones
    estimated_arrival = Column(DateTime, nullable=True)
    estimated_duration = Column(Integer, nullable=True)  # minutos
    
    # Información del cliente
    customer_phone = Column(String(20), nullable=True)
    customer_name = Column(String(100), nullable=True)
    delivery_notes = Column(Text, nullable=True)
    
    # Tracking
    last_location_update = Column(DateTime, nullable=True)
    distance_remaining = Column(Float, nullable=True)  # km
    
    # Relaciones
    order = relationship("Order", back_populates="delivery_tracking")
    driver = relationship("Driver", back_populates="deliveries")
    location_updates = relationship("LocationUpdate", back_populates="delivery")

class LocationUpdate(Base):
    """Modelo para historial de ubicaciones"""
    __tablename__ = "location_updates"
    
    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=False, index=True)
    delivery_id = Column(Integer, ForeignKey("delivery_tracking.id"), nullable=True, index=True)
    
    # Ubicación
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    accuracy = Column(Float, nullable=True)  # Precisión en metros
    speed = Column(Float, nullable=True)  # Velocidad en km/h
    heading = Column(Float, nullable=True)  # Dirección en grados
    
    # Timestamp
    timestamp = Column(DateTime, default=func.now(), nullable=False)
    
    # Relaciones
    driver = relationship("Driver", back_populates="location_updates")
    delivery = relationship("DeliveryTracking", back_populates="location_updates")

class DriverSession(Base):
    """Modelo para sesiones activas de conductores"""
    __tablename__ = "driver_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=False, index=True)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    
    # Estado de la sesión
    is_active = Column(Boolean, default=True, nullable=False)
    last_activity = Column(DateTime, default=func.now(), nullable=False)
    
    # Información de la sesión
    device_info = Column(JSON, nullable=True)  # {"platform": "android", "version": "1.0"}
    ip_address = Column(String(45), nullable=True)
    
    # Timestamps
    started_at = Column(DateTime, default=func.now(), nullable=False)
    ended_at = Column(DateTime, nullable=True)
    
    # Relaciones
    driver = relationship("Driver")
