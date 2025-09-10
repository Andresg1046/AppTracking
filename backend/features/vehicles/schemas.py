"""
Schemas para el módulo de vehículos
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
import base64


class VehicleStatus(str, Enum):
    """Estados posibles de un vehículo"""
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"
    RETIRED = "retired"


class VehicleBase(BaseModel):
    """Schema base para vehículos"""
    brand: str = Field(..., min_length=1, max_length=50, description="Marca del vehículo")
    model: str = Field(..., min_length=1, max_length=50, description="Modelo del vehículo")
    year: int = Field(..., ge=1900, le=2030, description="Año del vehículo")
    color: Optional[str] = Field(None, max_length=30, description="Color del vehículo")
    plate: str = Field(..., min_length=1, max_length=20, description="Placa del vehículo")
    state: str = Field(..., min_length=2, max_length=10, description="Estado de registro")
    photo: Optional[str] = Field(None, description="Foto del vehículo")
    status: VehicleStatus = Field(VehicleStatus.ACTIVE, description="Estado del vehículo")
    notes: Optional[str] = Field(None, description="Notas adicionales")

    @validator('plate')
    def validate_plate(cls, v):
        """Validar formato de placa"""
        if not v:
            raise ValueError('La placa no puede estar vacía')
        # Remover espacios y convertir a mayúsculas
        v = v.replace(' ', '').upper()
        if len(v) < 2:
            raise ValueError('La placa debe tener al menos 2 caracteres')
        return v

    @validator('state')
    def validate_state(cls, v):
        """Validar formato de estado"""
        if not v:
            raise ValueError('El estado no puede estar vacío')
        return v.upper()

    @validator('year')
    def validate_year(cls, v):
        """Validar año"""
        current_year = datetime.now().year
        if v < 1900 or v > current_year + 1:
            raise ValueError(f'El año debe estar entre 1900 y {current_year + 1}')
        return v


class VehicleCreate(VehicleBase):
    """Schema para crear un vehículo"""
    assigned_user_id: Optional[int] = Field(None, description="ID del usuario asignado")
    assigned_by: Optional[int] = Field(None, description="ID de quien asigna el vehículo")


class VehicleUpdate(BaseModel):
    """Schema para actualizar un vehículo"""
    brand: Optional[str] = Field(None, min_length=1, max_length=50)
    model: Optional[str] = Field(None, min_length=1, max_length=50)
    year: Optional[int] = Field(None, ge=1900, le=2030)
    color: Optional[str] = Field(None, max_length=30)
    plate: Optional[str] = Field(None, min_length=1, max_length=20)
    state: Optional[str] = Field(None, min_length=2, max_length=10)
    photo: Optional[str] = Field(None, description="Foto del vehículo")
    status: Optional[VehicleStatus] = None
    assigned_user_id: Optional[int] = None
    notes: Optional[str] = None

    @validator('plate')
    def validate_plate(cls, v):
        if v is not None:
            v = v.replace(' ', '').upper()
            if len(v) < 2:
                raise ValueError('La placa debe tener al menos 2 caracteres')
        return v

    @validator('state')
    def validate_state(cls, v):
        if v is not None:
            return v.upper()
        return v


class VehicleAssign(BaseModel):
    """Schema para asignar un vehículo a un usuario"""
    assigned_user_id: int = Field(..., description="ID del usuario a asignar")
    assigned_by: int = Field(..., description="ID de quien hace la asignación")
    notes: Optional[str] = Field(None, description="Notas de la asignación")


class VehicleResponse(VehicleBase):
    """Schema para respuesta de vehículo"""
    id: int
    assigned_user_id: Optional[int] = None
    assigned_at: Optional[datetime] = None
    assigned_by: Optional[int] = None
    is_active: bool
    created_by: int
    created_at: datetime
    updated_at: datetime

    # Información del usuario asignado
    assigned_user_name: Optional[str] = None
    assigned_user_email: Optional[str] = None

    # Información de quien asignó
    assigned_by_name: Optional[str] = None

    # Información del creador
    creator_name: Optional[str] = None

    # Foto para la respuesta
    photo: Optional[str] = None

    class Config:
        from_attributes = True


class VehicleListResponse(BaseModel):
    """Schema para lista de vehículos"""
    vehicles: List[VehicleResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class VehicleLookupRequest(BaseModel):
    """Schema para búsqueda de vehículo por placa"""
    plate: str = Field(..., min_length=1, max_length=20, description="Placa del vehículo")
    state: str = Field(..., min_length=2, max_length=10, description="Estado de registro")

    @validator('plate')
    def validate_plate(cls, v):
        v = v.replace(' ', '').upper()
        if len(v) < 2:
            raise ValueError('La placa debe tener al menos 2 caracteres')
        return v

    @validator('state')
    def validate_state(cls, v):
        return v.upper()


class VehicleLookupResponse(BaseModel):
    """Schema para respuesta de búsqueda de vehículo"""
    found: bool
    vehicle: Optional[VehicleResponse] = None
    message: str
