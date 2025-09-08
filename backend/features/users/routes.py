from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_current_user
from core.utils import format_datetime_for_response
from features.users.services import UserService
from features.users.models import User
from features.users.schemas import UserMeResponse

users_router = APIRouter()

@users_router.get("/me", response_model=UserMeResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Obtiene la información del usuario actual"""
    return UserMeResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        phone=current_user.phone,
        role={
            "id": current_user.role.id if current_user.role else None,
            "name": current_user.role.name if current_user.role else "unknown",
            "description": current_user.role.description if current_user.role else None
        },
        is_active=current_user.is_active,
        email_verified=current_user.email_verified,
        last_login=format_datetime_for_response(current_user.last_login),
        created_at=format_datetime_for_response(current_user.created_at),
        updated_at=format_datetime_for_response(current_user.updated_at)
    )

def require_admin_role(current_user: User = Depends(get_current_user)):
    """Verifica que el usuario actual tenga rol de administrador"""
    if not current_user.role or current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin role required."
        )
    return current_user

@users_router.get("/")
def get_users(
    current_user: User = Depends(require_admin_role),
    db: Session = Depends(get_db)
):
    """Obtiene todos los usuarios (solo administradores)"""
    users = UserService.get_all_users(db)
    return [
        {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "phone": user.phone,
            "role_id": user.role_id,
            "role": {
                "id": user.role.id if user.role else None,
                "name": user.role.name if user.role else "unknown"
            },
            "is_active": user.is_active,
            "email_verified": user.email_verified,
            "last_login": format_datetime_for_response(user.last_login),
            "created_at": format_datetime_for_response(user.created_at),
            "updated_at": format_datetime_for_response(user.updated_at)
        }
        for user in users
    ]

@users_router.post("/", status_code=201)
def create_user(
    user_data: dict,
    current_user: User = Depends(require_admin_role),
    db: Session = Depends(get_db)
):
    """Crea un nuevo usuario (solo administradores)"""
    try:
        user = UserService.create_user_with_role(user_data, db)
        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "phone": user.phone,
            "role_id": user.role_id,
            "role": {
                "id": user.role.id if user.role else None,
                "name": user.role.name if user.role else "unknown"
            },
            "is_active": user.is_active,
            "email_verified": user.email_verified,
            "last_login": format_datetime_for_response(user.last_login),
            "created_at": format_datetime_for_response(user.created_at),
            "updated_at": format_datetime_for_response(user.updated_at)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@users_router.get("/{user_id}")
def get_user(
    user_id: int,
    current_user: User = Depends(require_admin_role),
    db: Session = Depends(get_db)
):
    """Obtiene un usuario por ID (solo administradores)"""
    user = UserService.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "phone": user.phone,
        "role_id": user.role_id,
        "role": {
            "id": user.role.id if user.role else None,
            "name": user.role.name if user.role else "unknown"
        },
        "is_active": user.is_active,
        "email_verified": user.email_verified,
        "last_login": format_datetime_for_response(user.last_login),
        "created_at": format_datetime_for_response(user.created_at),
        "updated_at": format_datetime_for_response(user.updated_at)
    }

@users_router.put("/{user_id}")
def update_user(
    user_id: int,
    user_data: dict,
    current_user: User = Depends(require_admin_role),
    db: Session = Depends(get_db)
):
    """Actualiza un usuario (solo administradores)"""
    try:
        user = UserService.update_user(user_id, user_data, db)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "phone": user.phone,
            "role_id": user.role_id,
            "role": {
                "id": user.role.id if user.role else None,
                "name": user.role.name if user.role else "unknown"
            },
            "is_active": user.is_active,
            "email_verified": user.email_verified,
            "last_login": format_datetime_for_response(user.last_login),
            "created_at": format_datetime_for_response(user.created_at),
            "updated_at": format_datetime_for_response(user.updated_at)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@users_router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin_role),
    db: Session = Depends(get_db)
):
    """Elimina un usuario (solo administradores)"""
    success = UserService.delete_user(user_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    from fastapi import Response
    return Response(status_code=204)
