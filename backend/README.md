# Vehicle Tracking Backend API

Un sistema robusto de seguimiento de vehículos con autenticación completa, seguridad avanzada y escalabilidad optimizada.

## Características Principales

### Seguridad
- **Autenticación JWT** con tokens de acceso y refresh
- **Rate Limiting** para prevenir ataques de fuerza bruta
- **Bloqueo de cuentas** después de intentos fallidos
- **Logging de seguridad** completo
- **Headers de seguridad** HTTP
- **Validación de contraseñas** con políticas estrictas

### Rendimiento y Escalabilidad
- **Índices de base de datos** optimizados
- **Constraints de integridad** de datos
- **Conexiones de base de datos** eficientes
- **Middleware de logging** estructurado
- **WebSocket** para actualizaciones en tiempo real

### Arquitectura Sólida
- **Principios SOLID** aplicados
- **Separación de responsabilidades**
- **Inyección de dependencias**
- **Migraciones de base de datos** con Alembic
- **Configuración por variables de entorno**

## Instalación

### Prerrequisitos
- Python 3.8+
- PostgreSQL 12+
- pip

### 1. Clonar y configurar el entorno

```bash
# Navegar al directorio backend
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\\Scripts\\activate
# En Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

```bash
# Copiar archivo de ejemplo
cp env_example.txt .env

# Editar .env con tus configuraciones
```

**Variables importantes:**
```env
# Base de datos
DATABASE_URL=postgresql://postgres:password@172.16.1.116/tracking

# Seguridad
SECRET_KEY=tu-clave-secreta-super-segura-aqui
ADMIN_PASSWORD=Admin123!

# Configuración de la aplicación
DEBUG=True
LOG_LEVEL=INFO
```

### 3. Configurar la base de datos

```bash
# Opción 1: Inicialización automática (recomendado para desarrollo)
python init_db.py

# Opción 2: Usar migraciones (recomendado para producción)
python create_migration.py
alembic upgrade head
```

### 4. Ejecutar la aplicación

```bash
# Desarrollo
python main.py

# O con uvicorn directamente
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Producción
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Estructura del Proyecto

```
backend/
├── alembic/                 # Migraciones de base de datos
├── logs/                    # Archivos de log
├── auth.py                  # Sistema de autenticación
├── auth_endpoints.py        # Endpoints de autenticación
├── database.py              # Configuración de base de datos
├── models.py                # Modelos SQLAlchemy
├── schemas.py               # Esquemas Pydantic
├── security.py              # Middleware de seguridad
├── logging_config.py        # Configuración de logging
├── main.py                  # Aplicación principal
├── init_db.py              # Script de inicialización
├── create_migration.py      # Script de migración
├── requirements.txt         # Dependencias
└── README.md               # Este archivo
```

## API Endpoints

### Autenticación
- `POST /auth/register` - Registrar usuario
- `POST /auth/login` - Iniciar sesión
- `POST /auth/refresh` - Renovar token
- `POST /auth/logout` - Cerrar sesión
- `GET /auth/me` - Información del usuario actual
- `PUT /auth/me` - Actualizar perfil
- `POST /auth/change-password` - Cambiar contraseña

### Administración
- `GET /auth/users` - Listar usuarios (admin)
- `PUT /auth/users/{user_id}` - Actualizar usuario (admin)

### Seguimiento
- `POST /location` - Actualizar ubicación
- `GET /locations/{user_id}` - Obtener ubicaciones
- `WS /ws/{token}` - WebSocket para tiempo real

### Sistema
- `GET /health` - Estado del sistema

## Seguridad

### Políticas de Contraseñas
- Mínimo 8 caracteres
- Al menos una mayúscula
- Al menos una minúscula
- Al menos un dígito
- Al menos un carácter especial

### Rate Limiting
- 60 requests por minuto por IP
- 10 requests por segundo (burst)
- Headers de retry incluidos

### Logging de Seguridad
- Intentos de login (exitosos y fallidos)
- Cambios de contraseña
- Conexiones WebSocket
- Errores de autenticación

## Base de Datos

### Modelos Principales
- **User**: Usuarios del sistema (admin/driver)
- **RefreshToken**: Tokens de renovación
- **LoginLog**: Registro de intentos de login
- **Location**: Ubicaciones GPS
- **Vehicle**: Vehículos
- **Delivery**: Entregas

### Índices Optimizados
- Búsquedas por email y estado activo
- Consultas por rol y estado
- Ubicaciones por usuario y timestamp
- Tokens por usuario y expiración

## Desarrollo

### Crear nueva migración
```bash
python create_migration.py
```

### Ejecutar tests
```bash
pytest
```

### Verificar logs
```bash
# Logs de aplicación
tail -f logs/app.log

# Logs de seguridad
tail -f logs/security.log

# Logs de errores
tail -f logs/errors.log
```

## Producción

### Variables de entorno críticas
```env
DEBUG=False
SECRET_KEY=clave-super-secreta-de-produccion
DATABASE_URL=postgresql://user:pass@host:port/db
LOG_LEVEL=WARNING
```

### Configuración de servidor
- Usar HTTPS en producción
- Configurar proxy reverso (nginx)
- Monitorear logs de seguridad
- Backup regular de base de datos

## Monitoreo

### Métricas importantes
- Intentos de login fallidos
- Rate limiting activado
- Errores de base de datos
- Tiempo de respuesta de API
- Conexiones WebSocket activas

### Alertas recomendadas
- Múltiples intentos de login fallidos
- Rate limiting frecuente
- Errores de base de datos
- Tiempo de respuesta alto

## Soporte

Para problemas o preguntas:
1. Revisar logs en `logs/`
2. Verificar configuración de `.env`
3. Comprobar conectividad a base de datos
4. Revisar documentación de FastAPI

## Licencia

Este proyecto está bajo la licencia MIT.
