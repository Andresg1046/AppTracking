"""
Esquemas Pydantic para el sistema de tracking
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class DriverStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    AVAILABLE = "available"

class DeliveryStatus(str, Enum):
    ASSIGNED = "assigned"
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class DeliveryPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class LocationData(BaseModel):
    """Datos de ubicación"""
    lat: float = Field(..., ge=-90, le=90, description="Latitud")
    lng: float = Field(..., ge=-180, le=180, description="Longitud")
    accuracy: Optional[float] = Field(None, ge=0, description="Precisión en metros")
    speed: Optional[float] = Field(None, ge=0, description="Velocidad en km/h")
    heading: Optional[float] = Field(None, ge=0, le=360, description="Dirección en grados")
    timestamp: Optional[datetime] = Field(None, description="Timestamp de la ubicación")

class DriverActivateRequest(BaseModel):
    """Solicitud para activar conductor"""
    vehicle_id: Optional[int] = Field(None, description="ID del vehículo a asignar")
    driver_license: Optional[str] = Field(None, max_length=50, description="Número de licencia")
    phone: Optional[str] = Field(None, max_length=20, description="Teléfono del conductor")
    notes: Optional[str] = Field(None, description="Notas adicionales")
    location_update_interval: int = Field(30, ge=10, le=300, description="Intervalo de actualización en segundos")
    auto_location_sharing: bool = Field(True, description="Compartir ubicación automáticamente")

class DriverUpdateRequest(BaseModel):
    """Solicitud para actualizar perfil de conductor"""
    vehicle_id: Optional[int] = Field(None, description="ID del vehículo a asignar")
    driver_license: Optional[str] = Field(None, max_length=50, description="Número de licencia")
    phone: Optional[str] = Field(None, max_length=20, description="Teléfono del conductor")
    notes: Optional[str] = Field(None, description="Notas adicionales")
    location_update_interval: Optional[int] = Field(None, ge=10, le=300, description="Intervalo de actualización en segundos")
    auto_location_sharing: Optional[bool] = Field(None, description="Compartir ubicación automáticamente")

class DriverResponse(BaseModel):
    """Respuesta de perfil de conductor"""
    id: int
    user_id: int
    vehicle_id: Optional[int]
    is_online: bool
    is_available: bool
    is_delivering: bool
    current_location: Optional[LocationData]
    last_location_update: Optional[datetime]
    driver_license: Optional[str]
    phone: Optional[str]
    notes: Optional[str]
    location_update_interval: int
    auto_location_sharing: bool
    created_at: datetime
    updated_at: datetime
    
    # Información del usuario
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    user_phone: Optional[str] = None
    
    # Información del vehículo
    vehicle_info: Optional[Dict[str, Any]] = None
    
    # Estadísticas
    total_deliveries: Optional[int] = None
    completed_deliveries: Optional[int] = None
    success_rate: Optional[float] = None

class DriverListResponse(BaseModel):
    """Respuesta de lista de conductores"""
    drivers: List[DriverResponse]
    total: int
    online_count: int
    available_count: int
    delivering_count: int

class LocationUpdateRequest(BaseModel):
    """Solicitud de actualización de ubicación"""
    latitude: float = Field(..., ge=-90, le=90, description="Latitud")
    longitude: float = Field(..., ge=-180, le=180, description="Longitud")
    accuracy: Optional[float] = Field(None, ge=0, description="Precisión en metros")
    speed: Optional[float] = Field(None, ge=0, description="Velocidad en km/h")
    heading: Optional[float] = Field(None, ge=0, le=360, description="Dirección en grados")

class LocationUpdateResponse(BaseModel):
    """Respuesta de actualización de ubicación"""
    success: bool
    message: str
    timestamp: datetime
    location: LocationData
    distance_from_destination: Optional[float] = None
    estimated_arrival: Optional[datetime] = None

class DriverStatusUpdateRequest(BaseModel):
    """Solicitud de actualización de estado"""
    is_online: Optional[bool] = Field(None, description="Estado online/offline")
    is_available: Optional[bool] = Field(None, description="Disponibilidad para entregas")
    notes: Optional[str] = Field(None, description="Notas del cambio de estado")

class DriverStatusResponse(BaseModel):
    """Respuesta de estado del conductor"""
    driver_id: int
    is_online: bool
    is_available: bool
    is_delivering: bool
    current_location: Optional[LocationData]
    last_update: datetime
    status_message: str

class DeliveryTrackingCreate(BaseModel):
    """Solicitud para crear tracking de entrega"""
    order_id: int = Field(..., description="ID de la orden")
    driver_id: int = Field(..., description="ID del conductor")
    priority: DeliveryPriority = Field(DeliveryPriority.NORMAL, description="Prioridad de la entrega")
    delivery_notes: Optional[str] = Field(None, description="Notas de entrega")
    estimated_duration: Optional[int] = Field(None, ge=1, description="Duración estimada en minutos")

class DeliveryTrackingResponse(BaseModel):
    """Respuesta de tracking de entrega"""
    id: int
    order_id: int
    driver_id: int
    status: DeliveryStatus
    priority: DeliveryPriority
    assigned_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    delivery_address: Optional[Dict[str, Any]]
    delivery_coordinates: Optional[LocationData]
    estimated_arrival: Optional[datetime]
    estimated_duration: Optional[int]
    delivery_notes: Optional[str]
    customer_phone: Optional[str]
    customer_name: Optional[str]
    distance_remaining: Optional[float]
    last_location_update: Optional[datetime]
    
    # Información del conductor
    driver_info: Optional[Dict[str, Any]] = None
    
    # Información de la orden
    order_info: Optional[Dict[str, Any]] = None

class DeliveryStatusUpdate(BaseModel):
    """Solicitud de actualización de estado de entrega"""
    status: DeliveryStatus
    notes: Optional[str] = None
    location: Optional[LocationData] = None
    estimated_arrival: Optional[datetime] = None

class DriverLocationResponse(BaseModel):
    """Respuesta de ubicación de conductor para clientes"""
    driver_id: int
    driver_name: str
    driver_phone: Optional[str]
    is_online: bool
    is_delivering: bool
    current_location: Optional[LocationData]
    last_update: datetime
    vehicle_info: Optional[Dict[str, Any]]
    estimated_arrival: Optional[datetime]
    status_message: str

class TrackingOrderResponse(BaseModel):
    """Respuesta de tracking de orden para cliente"""
    order_id: int
    order_number: str
    status: str
    driver: Optional[DriverLocationResponse]
    delivery_address: Dict[str, Any]
    estimated_arrival: Optional[datetime]
    tracking_enabled: bool
    last_update: datetime

class AdminDashboardResponse(BaseModel):
    """Respuesta del dashboard de administración"""
    total_drivers: int
    online_drivers: int
    available_drivers: int
    delivering_drivers: int
    total_deliveries: int
    active_deliveries: int
    completed_deliveries_today: int
    drivers: List[DriverResponse]
    recent_deliveries: List[DeliveryTrackingResponse]

class DriverStatsResponse(BaseModel):
    """Estadísticas de conductor"""
    driver_id: int
    total_deliveries: int
    completed_deliveries: int
    failed_deliveries: int
    success_rate: float
    average_delivery_time: Optional[float]
    total_distance: Optional[float]
    rating: Optional[float]
    last_30_days: Dict[str, Any]
