from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    phone: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    phone: str
    role_id: int
    is_active: bool
    email_verified: bool
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime

class UserMeResponse(BaseModel):
    id: int
    email: str
    full_name: str
    phone: str
    role: dict
    is_active: bool
    email_verified: bool
    last_login: Optional[str]
    created_at: str
    updated_at: str

class UserListResponse(BaseModel):
    id: int
    email: str
    full_name: str
    phone: str
    role_id: int
    role_name: str
    is_active: bool
    email_verified: bool
    last_login: Optional[str]
    created_at: str
    updated_at: str

class UsersGroupedResponse(BaseModel):
    total_users: int
    roles: dict

class UserCreateRequest(BaseModel):
    full_name: str
    email: str
    phone: str
    role_id: int
    password: str

class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    role_id: Optional[int] = None
    is_active: Optional[bool] = None

class UserPasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

# Esquema unificado para respuestas de usuario
class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    phone: str
    role_id: int
    role_name: str
    is_active: bool
    email_verified: bool
    last_login: Optional[str]
    created_at: str
    updated_at: str
