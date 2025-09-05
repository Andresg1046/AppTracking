from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_current_user
from features.auth.schemas import UserLogin, TokenResponse, ForgotPasswordRequest, ResetPasswordRequest, LogoutResponse
from features.users.schemas import UserCreate
from features.auth.services import AuthService
from features.users.services import UserService
from features.users.models import User

auth_router = APIRouter()

@auth_router.post("/register", response_model=dict)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Registra un nuevo usuario"""
    # Verificar si el email ya existe
    existing_user = UserService.get_user_by_email(user.email, db)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Crear usuario
    db_user = UserService.create_user(user.dict(), db)
    
    # Obtener el nombre del rol
    role_name = db_user.role.name if db_user.role else "unknown"
    
    return {
        "message": "User created successfully",
        "role": role_name,
        "is_first_user": db.query(User).count() == 1
    }

@auth_router.post("/login", response_model=TokenResponse)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Inicia sesión de usuario"""
    user = AuthService.authenticate_user(user_credentials.email, user_credentials.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Actualizar last_login
    AuthService.update_last_login(user, db)
    
    # Crear token
    access_token = AuthService.create_token(user)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=1800
    )

@auth_router.post("/logout", response_model=LogoutResponse)
def logout(current_user: User = Depends(get_current_user)):
    """Cierra la sesión del usuario actual"""
    # En un sistema más avanzado, aquí se invalidaría el token
    # Por ahora, solo retornamos un mensaje de éxito
    return LogoutResponse(message="Sesión cerrada exitosamente")

@auth_router.post("/forgot-password", response_model=dict)
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Solicita restablecer contraseña"""
    reset_code = AuthService.create_password_reset(request.email, db)
    
    if not reset_code:
        raise HTTPException(
            status_code=404,
            detail="Email no encontrado"
        )
    
    # En producción, aquí se enviaría el código por email
    # Por ahora, lo retornamos en la respuesta para pruebas
    return {
        "message": "Código de restablecimiento enviado",
        "reset_code": reset_code,  # Solo para desarrollo
        "expires_in_minutes": 15
    }

@auth_router.post("/reset-password", response_model=dict)
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Restablece la contraseña con el código"""
    success = AuthService.reset_password(
        request.email, 
        request.reset_code, 
        request.new_password, 
        db
    )
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Código inválido o expirado"
        )
    
    return {
        "message": "Contraseña restablecida exitosamente"
    }
