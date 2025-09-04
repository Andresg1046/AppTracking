from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: str
    full_name: str
    role: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class LocationBase(BaseModel):
    latitude: float
    longitude: float
    accuracy: Optional[float] = None
    speed: Optional[float] = None
    heading: Optional[float] = None

class LocationCreate(LocationBase):
    pass

class Location(LocationBase):
    id: int
    user_id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class DeliveryBase(BaseModel):
    customer_name: str
    customer_address: str
    customer_phone: Optional[str] = None
    pickup_location: Optional[str] = None
    delivery_location: str

class DeliveryCreate(DeliveryBase):
    pass

class Delivery(DeliveryBase):
    id: int
    driver_id: int
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class VehicleBase(BaseModel):
    plate_number: str
    model: str
    brand: str
    year: int

class VehicleCreate(VehicleBase):
    pass

class Vehicle(VehicleBase):
    id: int
    driver_id: Optional[int] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
