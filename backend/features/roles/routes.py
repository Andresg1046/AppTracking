from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_current_user
from features.roles.services import RoleService
from features.roles.schemas import RoleResponse, RoleCreateRequest, RoleUpdateRequest
from features.users.models import User

roles_router = APIRouter()

def require_admin_role(current_user: User = Depends(get_current_user)):
    """Verifica que el usuario actual tenga rol de administrador"""
    if not current_user.role or current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin role required."
        )
    return current_user

@roles_router.get("/", response_model=list[RoleResponse])
def get_roles(
    current_user: User = Depends(require_admin_role),
    db: Session = Depends(get_db)
):
    """Obtiene todos los roles (solo administradores)"""
    roles = RoleService.get_all_roles(db)
    return roles

@roles_router.post("/", response_model=RoleResponse)
def create_role(
    role_data: RoleCreateRequest,
    current_user: User = Depends(require_admin_role),
    db: Session = Depends(get_db)
):
    """Crea un nuevo rol (solo administradores)"""
    try:
        new_role = RoleService.create_role(role_data.dict(), db)
        return RoleResponse(
            id=new_role.id,
            name=new_role.name,
            description=new_role.description,
            created_at=new_role.created_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@roles_router.get("/{role_id}", response_model=RoleResponse)
def get_role(
    role_id: int,
    current_user: User = Depends(require_admin_role),
    db: Session = Depends(get_db)
):
    """Obtiene un rol específico (solo administradores)"""
    role = RoleService.get_role_by_id(role_id, db)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    return RoleResponse(
        id=role.id,
        name=role.name,
        description=role.description,
        created_at=role.created_at
    )

@roles_router.put("/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: int,
    role_data: RoleUpdateRequest,
    current_user: User = Depends(require_admin_role),
    db: Session = Depends(get_db)
):
    """Actualiza un rol (solo administradores)"""
    try:
        # Filtrar campos None
        update_data = {k: v for k, v in role_data.dict().items() if v is not None}
        
        updated_role = RoleService.update_role(role_id, update_data, db)
        return RoleResponse(
            id=updated_role.id,
            name=updated_role.name,
            description=updated_role.description,
            created_at=updated_role.created_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@roles_router.delete("/{role_id}")
def delete_role(
    role_id: int,
    current_user: User = Depends(require_admin_role),
    db: Session = Depends(get_db)
):
    """Elimina un rol (solo administradores)"""
    try:
        RoleService.delete_role(role_id, db)
        return {"message": "Role deleted successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
