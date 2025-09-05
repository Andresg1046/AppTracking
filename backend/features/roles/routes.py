from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from features.roles.services import RoleService

roles_router = APIRouter()

@roles_router.get("/")
def get_roles(db: Session = Depends(get_db)):
    """Obtiene todos los roles"""
    roles = RoleService.get_all_roles(db)
    return roles
