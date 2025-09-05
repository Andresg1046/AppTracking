"""
Script de despliegue para producción
Configura automáticamente la BD y la aplicación
"""
import os
import sys
from dotenv import load_dotenv

def check_environment():
    """Verifica que el entorno esté configurado correctamente"""
    load_dotenv()
    
    required_vars = [
        "DATABASE_URL",
        "SECRET_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Variables de entorno faltantes: {', '.join(missing_vars)}")
        print("📝 Crea un archivo .env con las variables necesarias")
        return False
    
    print("✅ Variables de entorno configuradas correctamente")
    return True

def run_deployment():
    """Ejecuta el proceso de despliegue completo"""
    print("🚀 Iniciando despliegue...")
    
    # 1. Verificar entorno
    if not check_environment():
        sys.exit(1)
    
    # 2. Ejecutar migraciones
    try:
        from migrations import run_migrations, get_database_info
        print("Ejecutando migraciones...")
        run_migrations()
        
        # 3. Verificar estado
        info = get_database_info()
        print(f"Estado de la BD: {info}")
        
        print("Despliegue completado exitosamente")
        print("La aplicación está lista para usar")
        
    except Exception as e:
        print(f"Error durante el despliegue: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_deployment()
