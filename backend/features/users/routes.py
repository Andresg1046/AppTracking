from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from features.users.services import UserService

users_router = APIRouter()

@users_router.get("/")
def get_users(db: Session = Depends(get_db)):
    """Obtiene todos los usuarios"""
    users = UserService.get_all_users(db)
    return users
