from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RoleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime

class RoleCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None

class RoleUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None