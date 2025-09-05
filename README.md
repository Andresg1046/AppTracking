# Vehicle Tracking App

Aplicación móvil para tracking de vehículos en tiempo real. Permite a los conductores compartir su ubicación GPS y a los administradores monitorear la flota de vehículos.

## Características

- **Tracking GPS en tiempo real** para conductores
- **Panel de administrador** para monitorear todos los vehículos
- **Autenticación JWT** segura
- **Multiplataforma** (iOS y Android)
- **Comunicación en tiempo real** via WebSockets
- **Base de datos PostgreSQL**

## Arquitectura

- **Frontend**: Flutter (iOS/Android)
- **Backend**: Python FastAPI
- **Base de datos**: PostgreSQL
- **Comunicación**: HTTP REST + WebSockets

## Instalación

### Prerrequisitos

1. **Flutter SDK** (versión 3.35.1 o superior)
2. **Python 3.8+**
3. **PostgreSQL**
4. **Android Studio** (para desarrollo Android)

### Backend (Python/FastAPI)

1. **Navegar al directorio backend:**
```bash
cd backend
```

2. **Crear entorno virtual:**
```bash
python3 -m venv venv
```

3. **Activar entorno virtual:**
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

4. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

5. **Configurar base de datos:**
   - Crear base de datos PostgreSQL llamada `vehicle_tracking`
   - Copiar `env_example.txt` a `.env`
   - Actualizar `DATABASE_URL` en `.env` con tus credenciales

6. **Ejecutar migraciones:**
```bash
# Las tablas se crean automáticamente al ejecutar la aplicación
```

7. **Ejecutar el servidor:**
```bash
python3 main.py
```

El backend estará disponible en `http://localhost:8000`

### Frontend (Flutter)

1. **Navegar al directorio frontend:**
```bash
cd frontend/vehicle_tracking_app
```

2. **Instalar dependencias:**
```bash
flutter pub get
```

3. **Ejecutar la aplicación:**
```bash
flutter run
```

## Configuración

### Variables de Entorno (.env)

```env
DATABASE_URL=postgresql://username:password@localhost/vehicle_tracking
SECRET_KEY=your-super-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Permisos Android

Agregar los siguientes permisos en `android/app/src/main/AndroidManifest.xml`:

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_BACKGROUND_LOCATION" />
```

### Permisos iOS

Agregar en `ios/Runner/Info.plist`:

```xml
<key>NSLocationWhenInUseUsageDescription</key>
<string>Esta aplicación necesita acceso a la ubicación para tracking de vehículos</string>
<key>NSLocationAlwaysAndWhenInUseUsageDescription</key>
<string>Esta aplicación necesita acceso a la ubicación para tracking de vehículos</string>
```

## Uso

### Para Conductores

1. Iniciar sesión con credenciales de conductor
2. La aplicación solicitará permisos de ubicación
3. Presionar "Start Tracking" para comenzar a compartir ubicación
4. La ubicación se actualiza automáticamente cada 30 segundos

### Para Administradores

1. Iniciar sesión con credenciales de administrador
2. Ver dashboard con lista de todos los conductores
3. Ver estadísticas de vehículos activos
4. Monitorear ubicaciones en tiempo real

## API Endpoints

### Autenticación
- `POST /register` - Registrar nuevo usuario
- `POST /login` - Iniciar sesión

### Tracking
- `POST /location` - Actualizar ubicación
- `GET /locations/{user_id}` - Obtener ubicaciones de usuario
- `GET /users` - Obtener lista de usuarios (admin)

### WebSocket
- `WS /ws/{token}` - Conexión en tiempo real

## Estructura del Proyecto

```
├── backend/
│   ├── main.py              # Aplicación FastAPI
│   ├── database.py          # Configuración de BD
│   ├── models.py            # Modelos SQLAlchemy
│   ├── schemas.py           # Esquemas Pydantic
│   ├── auth.py              # Autenticación JWT
│   └── requirements.txt     # Dependencias Python
├── frontend/
│   └── vehicle_tracking_app/
│       ├── lib/
│       │   ├── models/      # Modelos Flutter
│       │   ├── services/    # Servicios API
│       │   ├── screens/     # Pantallas
│       │   ├── providers/   # State management
│       │   └── main.dart    # Punto de entrada
│       └── pubspec.yaml     # Dependencias Flutter
└── README.md
```

## Desarrollo

### Agregar Nuevas Funcionalidades

1. **Backend**: Agregar endpoints en `main.py`
2. **Frontend**: Crear nuevas pantallas en `lib/screens/`
3. **Base de datos**: Agregar modelos en `models.py`

### Testing

```bash
# Backend
cd backend
python -m pytest

# Frontend
cd frontend/vehicle_tracking_app
flutter test
```

## Despliegue

### Backend
- Usar Gunicorn para producción
- Configurar variables de entorno
- Usar base de datos PostgreSQL en la nube

### Frontend
- Generar APK: `flutter build apk`
- Generar IPA: `flutter build ios`
- Publicar en stores

## Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## Soporte

Para soporte técnico, contactar al equipo de desarrollo.
