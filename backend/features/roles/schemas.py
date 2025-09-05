from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RoleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
