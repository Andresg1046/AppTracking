from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_current_user, security
from core.utils import format_datetime_for_response
from core.config import settings
from features.auth.schemas import UserLogin, TokenResponse, RefreshTokenRequest, ForgotPasswordRequest, ResetPasswordRequest, LogoutResponse
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
def login(user_credentials: UserLogin, request: Request, db: Session = Depends(get_db)):
    """Inicia sesión de usuario - OPTIMIZADO"""
    email = user_credentials.email
    password = user_credentials.password
    
    # Obtener IP del cliente
    client_ip = request.client.host if request.client else "unknown"
    
    # OPTIMIZACIÓN: Una sola consulta para obtener usuario y verificar bloqueo
    user, is_locked, remaining_attempts = AuthService.authenticate_user_optimized(email, password, db)
    
    if is_locked:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Account locked due to too many failed attempts. Try again in 15 minutes.",
        )
    
    if not user:
        # Usuario no existe o contraseña incorrecta
        if remaining_attempts == 0:
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Account locked due to too many failed attempts. Try again in 15 minutes.",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Incorrect email or password. {remaining_attempts} attempts remaining.",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    # OPTIMIZACIÓN: Crear tokens y sesión en una sola operación
    access_token, refresh_token = AuthService.create_tokens_and_session(user, client_ip, db)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user={
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "phone": user.phone,
            "role": user.role.name if user.role else "unknown",
            "role_id": user.role_id,
            "is_active": user.is_active,
            "email_verified": user.email_verified,
            "last_login": format_datetime_for_response(user.last_login)
        }
    )

@auth_router.post("/logout", response_model=LogoutResponse)
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cierra la sesión del usuario actual"""
    token = credentials.credentials
    
    # Invalidar la sesión actual
    AuthService.invalidate_session_by_token(token, db)
    
    return LogoutResponse(message="Sesión cerrada exitosamente")

@auth_router.post("/refresh", response_model=TokenResponse)
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Renueva un access token usando el refresh token"""
    new_access_token = AuthService.refresh_access_token(request.refresh_token, db)
    
    if not new_access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Obtener información del usuario desde el token
    from core.security import verify_access_token
    email = verify_access_token(new_access_token)
    user = db.query(User).filter(User.email == email).first()
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=request.refresh_token,  # El refresh token sigue siendo el mismo
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convertir minutos a segundos
        user={
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "phone": user.phone,
            "role": user.role.name if user.role else "unknown",
            "role_id": user.role_id,
            "is_active": user.is_active,
            "email_verified": user.email_verified,
            "last_login": format_datetime_for_response(user.last_login)
        }
    )

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
