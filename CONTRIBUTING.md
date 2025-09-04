# Guía de Contribución - Vehicle Tracking App

## Estructura del Equipo

- **Backend Developer**:  - Python/FastAPI
- **Frontend Developer**:  - Flutter

## Flujo de Trabajo

### 1. Configuración Inicial

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/vehicle-tracking-app.git
cd vehicle-tracking-app

# Configurar backend
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
copy env_example.txt .env
# Editar .env con tus credenciales

# Configurar frontend
cd ../frontend/vehicle_tracking_app
flutter pub get
```

### 2. Desarrollo

#### Para Backend Developer:
- Trabajar en la carpeta `backend/`
- Crear nuevos endpoints en `main.py`
- Agregar modelos en `models.py`
- Actualizar esquemas en `schemas.py`
- Documentar cambios en la API

#### Para Frontend Developer:
- Trabajar en la carpeta `frontend/vehicle_tracking_app/`
- Crear nuevas pantallas en `lib/screens/`
- Agregar servicios en `lib/services/`
- Actualizar modelos en `lib/models/`
- Mantener consistencia en el diseño

### 3. Convenciones de Código

#### Python (Backend):
- Usar snake_case para variables y funciones
- Usar PascalCase para clases
- Documentar funciones con docstrings
- Seguir PEP 8

#### Dart (Frontend):
- Usar camelCase para variables y funciones
- Usar PascalCase para clases
- Documentar funciones con comentarios
- Seguir las convenciones de Flutter

### 4. Commits y Branches

#### Naming de Branches:
- `feature/nombre-funcionalidad` - Nuevas características
- `fix/nombre-bug` - Correcciones de bugs
- `refactor/nombre-refactorizacion` - Refactorización
- `docs/nombre-documentacion` - Documentación

#### Naming de Commits:
- `feat: agregar endpoint de usuarios`
- `fix: corregir error de autenticación`
- `refactor: reorganizar estructura de carpetas`
- `docs: actualizar README`

### 5. Pull Requests

1. Crear branch desde `main`
2. Desarrollar funcionalidad
3. Hacer commit con mensaje descriptivo
4. Crear Pull Request
5. Solicitar review al compañero
6. Merge después de aprobación

### 6. Testing

#### Backend:
```bash
cd backend
python -m pytest
```

#### Frontend:
```bash
cd frontend/vehicle_tracking_app
flutter test
```

### 7. Comunicación

- Usar Issues de GitHub para bugs y features
- Comunicar cambios importantes en Slack/Discord
- Documentar decisiones de arquitectura
- Mantener actualizado el README

## Estructura de Archivos

```
vehicle-tracking-app/
├── backend/                 # Tu responsabilidad
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── auth.py
│   ├── database.py
│   └── requirements.txt
├── frontend/               # Responsabilidad de tu compañero
│   └── vehicle_tracking_app/
│       ├── lib/
│       │   ├── screens/
│       │   ├── services/
│       │   ├── models/
│       │   └── main.dart
│       └── pubspec.yaml
├── docs/                   # Documentación compartida
├── README.md
└── CONTRIBUTING.md
```

## API Documentation

La API está documentada automáticamente en:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoints Principales

- `POST /login` - Autenticación
- `POST /register` - Registro
- `POST /location` - Actualizar ubicación
- `GET /users` - Listar usuarios (admin)
- `GET /locations/{user_id}` - Obtener ubicaciones

## Variables de Entorno

Crear archivo `.env` en `backend/`:
```env
DATABASE_URL=postgresql://username:password@localhost/vehicle_tracking
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Troubleshooting

### Problemas Comunes:

1. **Error de conexión a BD**: Verificar PostgreSQL y credenciales
2. **Error de dependencias**: Ejecutar `pip install -r requirements.txt`
3. **Error de Flutter**: Ejecutar `flutter clean && flutter pub get`
4. **Error de permisos**: Verificar AndroidManifest.xml e Info.plist

### Logs:
- Backend: Consola donde ejecutas `python main.py`
- Frontend: `flutter logs`

## Contacto

- Backend: [Tu email]
- Frontend: [Email de tu compañero]
- Slack/Discord: [Canal del proyecto]
