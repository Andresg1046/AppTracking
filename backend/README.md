# 🚀 Vehicle Tracking Backend

API backend para aplicación móvil de seguimiento de vehículos con sistema de autenticación completo.

## 📁 Estructura del Proyecto

```
backend/
├── app/
│   ├── __init__.py
│   └── main.py              # Aplicación principal FastAPI
├── features/
│   ├── auth/                # Módulo de autenticación
│   │   ├── models.py        # Modelos de BD (vacío)
│   │   ├── schemas.py       # Esquemas de validación
│   │   ├── routes.py        # Endpoints de auth
│   │   └── services.py      # Lógica de negocio
│   ├── users/               # Módulo de usuarios
│   │   ├── models.py        # Modelo User
│   │   ├── schemas.py       # Esquemas de usuario
│   │   ├── routes.py        # Endpoints de usuarios
│   │   └── services.py      # Servicios de usuario
│   └── roles/               # Módulo de roles
│       ├── models.py        # Modelo Role
│       ├── schemas.py       # Esquemas de rol
│       ├── routes.py        # Endpoints de roles
│       └── services.py      # Servicios de rol
├── core/
│   ├── database.py         # Configuración de BD
│   ├── security.py         # JWT y seguridad
│   └── migrations.py       # Migraciones automáticas
├── shared/                  # Código compartido
├── main.py                 # Punto de entrada
├── requirements.txt        # Dependencias
├── .env                    # Variables de entorno
└── env_example.txt         # Ejemplo de configuración
```

## 🚀 Instalación y Configuración

### 1. Requisitos Previos
- **Python 3.8+**
- **PostgreSQL** instalado y corriendo
- **Git** (opcional)

### 2. Configuración del Entorno

#### Crear entorno virtual:
```bash
python -m venv venv
```

#### Activar entorno virtual:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

#### Instalar dependencias:
```bash
pip install -r requirements.txt
```

### 3. Configuración de Base de Datos

#### Crear archivo `.env`:
```bash
# Copiar el ejemplo
cp env_example.txt .env
```

#### Editar `.env` con tus datos:
```env
DATABASE_URL=postgresql://usuario:contraseña@localhost/nombre_bd
SECRET_KEY=tu-clave-secreta-super-segura
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 4. Ejecutar la Aplicación

```bash
python main.py
```

**¡Eso es todo!** La aplicación se ejecutará automáticamente y:
- ✅ Creará/actualizará las tablas de BD
- ✅ Creará los roles por defecto (admin, driver)
- ✅ Iniciará el servidor en `http://localhost:8000`

## 📋 Endpoints Disponibles

### 🔐 Autenticación (`/auth`)
- **`POST /auth/register`** - Registro de usuario
- **`POST /auth/login`** - Inicio de sesión

### 👥 Usuarios (`/users`)
- **`GET /users/`** - Lista todos los usuarios

### 🎭 Roles (`/roles`)
- **`GET /roles/`** - Lista todos los roles

### 🏥 Sistema (`/`)
- **`GET /health`** - Estado de la aplicación

## 🧪 Pruebas con Postman/Insomnia

### Registro de Usuario:
```json
POST http://localhost:8000/auth/register
Content-Type: application/json

{
  "email": "admin@test.com",
  "password": "admin123",
  "full_name": "Admin Test",
  "phone": "1234567890"
}
```

### Login:
```json
POST http://localhost:8000/auth/login
Content-Type: application/json

{
  "email": "admin@test.com",
  "password": "admin123"
}
```

## 🔧 Características Técnicas

### Sistema de Roles Automático:
- **Primer usuario** → Rol `admin`
- **Usuarios siguientes** → Rol `driver`

### Seguridad:
- **JWT Tokens** con expiración de 30 minutos
- **Contraseñas hasheadas** con bcrypt
- **CORS** configurado para desarrollo

### Migraciones Automáticas:
- Se ejecutan al iniciar la aplicación
- Crean tablas y roles por defecto
- Verifican estructura de BD

## 🐛 Solución de Problemas

### Error: "No module named 'core'"
```bash
# Asegúrate de estar en el directorio backend
cd backend
python main.py
```

### Error: "Database connection failed"
- Verifica que PostgreSQL esté corriendo
- Revisa la URL de conexión en `.env`
- Verifica credenciales de la BD

### Error: "Table already exists"
```bash
# Recrear BD completamente
python -c "from core.database import engine; from core.database import Base; Base.metadata.drop_all(bind=engine); Base.metadata.create_all(bind=engine)"
python main.py
```

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs de la aplicación
2. Verifica la configuración de `.env`
3. Asegúrate de que PostgreSQL esté corriendo
4. Ejecuta `python main.py` para diagnóstico completo

## 🚀 Próximos Pasos

- [ ] Implementar logout
- [ ] Restablecer contraseña
- [ ] Verificación de email
- [ ] Límite de intentos de login
- [ ] Gestión de sesiones
- [ ] Funcionalidades de admin