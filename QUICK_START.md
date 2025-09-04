# Quick Start Guide - Vehicle Tracking App

## Setup Rápido (5 minutos)

### 1. Configurar Base de Datos PostgreSQL

1. Crear base de datos:
```sql
CREATE DATABASE vehicle_tracking;
```

2. Copiar archivo de configuración:
```bash
cd backend
copy env_example.txt .env
```

3. Editar `.env` con tus credenciales:
```env
DATABASE_URL=postgresql://tu_usuario:tu_password@localhost/vehicle_tracking
SECRET_KEY=mi-clave-secreta-super-segura
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 2. Ejecutar Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python init_db.py  # Crear usuarios de prueba
python main.py
```

### 3. Ejecutar Frontend

```bash
cd frontend/vehicle_tracking_app
flutter pub get
flutter run
```

## Usuarios de Prueba

- **Admin**: admin@company.com / admin123
- **Conductor 1**: driver1@company.com / driver123
- **Conductor 2**: driver2@company.com / driver123

## Testing Rápido

### Como Conductor:
1. Iniciar sesión con driver1@company.com / driver123
2. Permitir acceso a ubicación
3. Presionar "Start Tracking"
4. Ver ubicación actualizada

### Como Administrador:
1. Iniciar sesión con admin@company.com / admin123
2. Ver dashboard con lista de conductores
3. Ver estadísticas de vehículos

## Endpoints API

- **Login**: POST http://localhost:8000/login
- **Register**: POST http://localhost:8000/register
- **Update Location**: POST http://localhost:8000/location
- **Get Users**: GET http://localhost:8000/users

## Troubleshooting

### Error de conexión a base de datos:
- Verificar que PostgreSQL esté corriendo
- Verificar credenciales en `.env`
- Verificar que la base de datos `vehicle_tracking` exista

### Error de permisos de ubicación:
- Verificar que los permisos estén configurados en AndroidManifest.xml
- En iOS, verificar Info.plist

### Error de dependencias Flutter:
```bash
flutter clean
flutter pub get
```

## Próximos Pasos

1. **Configurar Google Maps API** para mapas en tiempo real
2. **Implementar WebSockets** para actualizaciones en tiempo real
3. **Agregar funcionalidad de entregas**
4. **Implementar notificaciones push**
5. **Agregar reportes y analytics**

## Soporte

Para problemas técnicos, revisar:
- Logs del backend en la consola
- Logs de Flutter con `flutter logs`
- Verificar conectividad de red
