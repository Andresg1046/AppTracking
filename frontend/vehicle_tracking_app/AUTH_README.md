# Sistema de Autenticación - Vehicle Tracking App

## Descripción

Este proyecto incluye un sistema completo de autenticación para la aplicación de seguimiento de vehículos, implementado con Flutter y conectado a un backend FastAPI.

## Características

### 🔐 Autenticación
- **Login**: Inicio de sesión con email y contraseña
- **Registro**: Creación de nuevas cuentas de usuario
- **Logout**: Cierre de sesión seguro
- **Persistencia**: Los tokens se almacenan localmente usando SharedPreferences
- **Refresh Token**: Renovación automática de tokens de acceso

### 🎨 Interfaz de Usuario
- **Diseño moderno**: UI limpia y profesional con Material Design 3
- **Validación de formularios**: Validación en tiempo real de campos
- **Manejo de errores**: Mensajes de error claros y user-friendly
- **Estados de carga**: Indicadores de progreso durante las operaciones
- **Responsive**: Adaptable a diferentes tamaños de pantalla

### 🏗️ Arquitectura
- **Provider Pattern**: Gestión de estado con Provider
- **Separación de responsabilidades**: Modelos, servicios y UI separados
- **Servicios HTTP**: Comunicación con API REST
- **Almacenamiento local**: Persistencia de datos de usuario

## Estructura del Proyecto

```
lib/
├── models/                 # Modelos de datos
│   ├── user.dart          # Modelo de usuario
│   ├── auth_response.dart # Respuesta de autenticación
│   ├── login_request.dart # Solicitud de login
│   └── register_request.dart # Solicitud de registro
├── services/              # Servicios de API
│   └── auth_service.dart  # Servicio de autenticación
├── providers/             # Gestión de estado
│   └── auth_provider.dart # Provider de autenticación
├── screens/               # Pantallas de la aplicación
│   ├── auth/             # Pantallas de autenticación
│   │   ├── login_screen.dart
│   │   └── register_screen.dart
│   └── home/             # Pantalla principal
│       └── home_screen.dart
├── widgets/               # Widgets reutilizables
│   ├── custom_text_field.dart
│   └── custom_button.dart
└── main.dart             # Punto de entrada de la aplicación
```

## Configuración

### 1. Backend URL
Actualiza la URL del backend en `lib/services/auth_service.dart`:

```dart
static const String baseUrl = 'http://tu-backend-url:8000';
```

### 2. Endpoints del Backend
El servicio espera los siguientes endpoints:
- `POST /auth/login` - Login de usuario
- `POST /auth/register` - Registro de usuario
- `POST /auth/refresh` - Renovar token
- `POST /auth/logout` - Cerrar sesión
- `GET /auth/me` - Obtener información del usuario actual

### 3. Formato de Respuesta
El backend debe devolver respuestas en el siguiente formato:

**Login/Register Response:**
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "user": {
    "id": "string",
    "email": "string",
    "name": "string",
    "phone": "string",
    "created_at": "ISO 8601",
    "updated_at": "ISO 8601"
  },
  "token_type": "Bearer",
  "expires_in": 3600
}
```

## Uso

### 1. Iniciar la Aplicación
```bash
flutter run
```

### 2. Flujo de Autenticación
1. **Primera vez**: La app muestra la pantalla de login
2. **Registro**: Los usuarios pueden crear una cuenta nueva
3. **Login**: Los usuarios existentes pueden iniciar sesión
4. **Home**: Después del login exitoso, se muestra la pantalla principal
5. **Logout**: Los usuarios pueden cerrar sesión desde el menú

### 3. Persistencia
- Los tokens se almacenan automáticamente al hacer login/registro
- La app verifica la autenticación al iniciar
- Si el token es válido, el usuario va directo a la pantalla principal
- Si el token expira, se intenta renovar automáticamente

## Dependencias Principales

- `provider`: Gestión de estado
- `http`: Cliente HTTP para API calls
- `shared_preferences`: Almacenamiento local
- `jwt_decoder`: Decodificación de tokens JWT

## Personalización

### Temas
Puedes personalizar el tema de la aplicación en `lib/main.dart`:

```dart
theme: ThemeData(
  colorScheme: ColorScheme.fromSeed(
    seedColor: const Color(0xFF1976D2), // Cambia este color
    brightness: Brightness.light,
  ),
  // ... más configuraciones
),
```

### Validaciones
Las validaciones de formularios se pueden modificar en las pantallas de login y registro.

### UI Components
Los widgets personalizados (`CustomTextField`, `CustomButton`) se pueden reutilizar en otras partes de la aplicación.

## Próximos Pasos

1. **Integración con Backend**: Conecta con tu API FastAPI
2. **Funcionalidades Adicionales**: Agrega las pantallas de vehículos, ubicaciones, etc.
3. **Mejoras de UX**: Agrega animaciones, mejor manejo de errores
4. **Testing**: Implementa tests unitarios y de integración
5. **Seguridad**: Agrega validaciones adicionales y manejo de errores de red

## Soporte

Para cualquier pregunta o problema, revisa la documentación de Flutter y las dependencias utilizadas.
