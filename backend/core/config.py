"""
Configuración global de la aplicación
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Base de datos
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost/vehicle_tracking")
    
    # Seguridad JWT
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    
    # Configuración de sesiones
    MAX_SESSIONS_PER_USER = int(os.getenv("MAX_SESSIONS_PER_USER", 3))
    
    # Configuración de seguridad - límite de intentos de login
    MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", 5))
    LOCKOUT_DURATION_MINUTES = int(os.getenv("LOCKOUT_DURATION_MINUTES", 15))
    
    # Rate limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE = int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", 60))
    
    # Configuración de la aplicación
    APP_NAME = os.getenv("APP_NAME", "Vehicle Tracking API")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

settings = Settings()
