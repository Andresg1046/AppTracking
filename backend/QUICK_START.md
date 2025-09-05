# ⚡ Inicio Rápido - Backend

## 🚀 Pasos para ejecutar el backend:

### 1. Configurar entorno virtual:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### 2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

### 3. Configurar base de datos:
```bash
# Copiar archivo de configuración
cp env_example.txt .env

# Editar .env con tus datos de PostgreSQL
```

### 4. Ejecutar aplicación:
```bash
python main.py
```

## ✅ ¡Listo!

La aplicación estará disponible en: `http://localhost:8000`

### Endpoints principales:
- **Registro:** `POST /auth/register`
- **Login:** `POST /auth/login`
- **Usuarios:** `GET /users/`
- **Roles:** `GET /roles/`
- **Estado:** `GET /health`

## 🧪 Probar registro:
```json
POST http://localhost:8000/auth/register
{
  "email": "admin@test.com",
  "password": "admin123",
  "full_name": "Admin Test",
  "phone": "1234567890"
}
```

**¡El primer usuario será automáticamente admin!** 🎯
