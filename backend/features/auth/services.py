from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets
import string
from features.users.models import User
from features.roles.models import Role
from features.auth.models import PasswordReset, UserSession, TokenBlacklist
from core.security import verify_password, create_access_token, get_password_hash
from core.config import settings

class AuthService:
    @staticmethod
    def authenticate_user(email: str, password: str, db: Session) -> User:
        """Autentica un usuario con email y contraseña"""
        user = db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user
    
    @staticmethod
    def create_token(user: User) -> str:
        """Crea un token JWT para el usuario"""
        return create_access_token(data={"sub": user.email})
    
    @staticmethod
    def create_refresh_token() -> str:
        """Crea un refresh token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def update_last_login(user: User, db: Session):
        """Actualiza el último login del usuario"""
        user.last_login = datetime.utcnow()
        db.commit()
    
    @staticmethod
    def generate_reset_code() -> str:
        """Genera un código de 6 dígitos para reset de contraseña"""
        return ''.join(secrets.choice(string.digits) for _ in range(6))
    
    @staticmethod
    def create_password_reset(email: str, db: Session) -> str:
        """Crea un código de reset de contraseña"""
        # Verificar que el usuario existe
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        
        # Generar código
        reset_code = AuthService.generate_reset_code()
        
        # Crear registro de reset
        password_reset = PasswordReset(
            email=email,
            reset_code=reset_code,
            expires_at=datetime.utcnow() + timedelta(minutes=15)  # 15 minutos
        )
        db.add(password_reset)
        db.commit()
        
        return reset_code
    
    @staticmethod
    def reset_password(email: str, reset_code: str, new_password: str, db: Session) -> bool:
        """Resetea la contraseña con el código"""
        # Buscar el reset válido
        password_reset = db.query(PasswordReset).filter(
            PasswordReset.email == email,
            PasswordReset.reset_code == reset_code,
            PasswordReset.is_used == False,
            PasswordReset.expires_at > datetime.utcnow()
        ).first()
        
        if not password_reset:
            return False
        
        # Actualizar contraseña del usuario
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.hashed_password = get_password_hash(new_password)
            password_reset.is_used = True
            db.commit()
            return True
        
        return False
    
    @staticmethod
    def create_session(user: User, access_token: str, refresh_token: str, device_info: str = None, ip_address: str = None, db: Session = None):
        """Crea una nueva sesión para el usuario"""
        # Verificar límite de sesiones
        active_sessions = db.query(UserSession).filter(
            UserSession.user_id == user.id,
            UserSession.is_active == True,
            UserSession.expires_at > datetime.utcnow()
        ).count()
        
        if active_sessions >= settings.MAX_SESSIONS_PER_USER:
            # Eliminar la sesión más antigua
            oldest_session = db.query(UserSession).filter(
                UserSession.user_id == user.id,
                UserSession.is_active == True
            ).order_by(UserSession.last_used.asc()).first()
            
            if oldest_session:
                AuthService.invalidate_session(oldest_session.id, db)
        
        # Crear nueva sesión
        session = UserSession(
            user_id=user.id,
            access_token=access_token,
            refresh_token=refresh_token,
            device_info=device_info,
            ip_address=ip_address,
            expires_at=datetime.utcnow() + timedelta(minutes=30)
        )
        db.add(session)
        db.commit()
        return session
    
    @staticmethod
    def invalidate_session(session_id: int, db: Session):
        """Invalida una sesión específica"""
        session = db.query(UserSession).filter(UserSession.id == session_id).first()
        if session:
            # Agregar token a blacklist
            blacklist_entry = TokenBlacklist(
                token=session.access_token,
                expires_at=session.expires_at
            )
            db.add(blacklist_entry)
            
            # Marcar sesión como inactiva
            session.is_active = False
            db.commit()
    
    @staticmethod
    def invalidate_all_sessions(user_id: int, db: Session):
        """Invalida todas las sesiones de un usuario"""
        sessions = db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.is_active == True
        ).all()
        
        for session in sessions:
            # Agregar token a blacklist
            blacklist_entry = TokenBlacklist(
                token=session.access_token,
                expires_at=session.expires_at
            )
            db.add(blacklist_entry)
            session.is_active = False
        
        db.commit()
    
    @staticmethod
    def is_token_blacklisted(token: str, db: Session) -> bool:
        """Verifica si un token está en la blacklist"""
        blacklisted = db.query(TokenBlacklist).filter(
            TokenBlacklist.token == token,
            TokenBlacklist.expires_at > datetime.utcnow()
        ).first()
        return blacklisted is not None
    
    @staticmethod
    def refresh_access_token(refresh_token: str, db: Session) -> str:
        """Renueva un access token usando el refresh token"""
        session = db.query(UserSession).filter(
            UserSession.refresh_token == refresh_token,
            UserSession.is_active == True,
            UserSession.expires_at > datetime.utcnow()
        ).first()
        
        if not session:
            return None
        
        # Crear nuevo access token
        user = db.query(User).filter(User.id == session.user_id).first()
        new_access_token = AuthService.create_token(user)
        
        # Actualizar sesión
        session.access_token = new_access_token
        session.last_used = datetime.utcnow()
        session.expires_at = datetime.utcnow() + timedelta(minutes=30)
        db.commit()
        
        return new_access_token
