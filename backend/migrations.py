"""
Sistema de migraciones automático
Se ejecuta al iniciar la aplicación para crear/actualizar la BD
"""
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from models import Base, Role, User
from auth import get_password_hash
import logging

logger = logging.getLogger(__name__)

def run_migrations():
    """Ejecuta todas las migraciones necesarias"""
    try:
        # 1. Crear todas las tablas
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tablas creadas/actualizadas")
        
        # 2. Crear roles por defecto
        create_default_roles()
        
        # 3. Verificar estructura
        verify_database_structure()
        
        logger.info("🎉 Migraciones completadas exitosamente")
        
    except Exception as e:
        logger.error(f"❌ Error en migraciones: {e}")
        raise

def create_default_roles():
    """Crea los roles por defecto si no existen"""
    db = SessionLocal()
    try:
        # Crear rol admin
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if not admin_role:
            admin_role = Role(name="admin", description="Administrator role")
            db.add(admin_role)
            logger.info("✅ Rol 'admin' creado")
        
        # Crear rol driver
        driver_role = db.query(Role).filter(Role.name == "driver").first()
        if not driver_role:
            driver_role = Role(name="driver", description="Driver role")
            db.add(driver_role)
            logger.info("✅ Rol 'driver' creado")
        
        db.commit()
        
    except Exception as e:
        logger.error(f"❌ Error creando roles: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def verify_database_structure():
    """Verifica que la estructura de la BD sea correcta"""
    db = SessionLocal()
    try:
        # Verificar que existen los roles
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        driver_role = db.query(Role).filter(Role.name == "driver").first()
        
        if not admin_role or not driver_role:
            raise Exception("Roles por defecto no encontrados")
        
        logger.info("✅ Estructura de BD verificada")
        
    except Exception as e:
        logger.error(f"❌ Error verificando estructura: {e}")
        raise
    finally:
        db.close()

def get_database_info():
    """Obtiene información del estado actual de la BD"""
    db = SessionLocal()
    try:
        user_count = db.query(User).count()
        role_count = db.query(Role).count()
        
        return {
            "users": user_count,
            "roles": role_count,
            "status": "ready"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
    finally:
        db.close()

if __name__ == "__main__":
    # Ejecutar migraciones manualmente
    run_migrations()
    info = get_database_info()
    print(f"📊 Estado de la BD: {info}")
