# Sistema de Impuestos - Documentación Completa

## 🏛️ Visión General

El sistema de impuestos implementado reemplaza completamente la funcionalidad básica del plugin WordPress y proporciona un manejo robusto y preciso de impuestos para e-commerce.

## 🎯 Características Principales

### ✅ **Cálculo Automático de Impuestos**
- **Impuestos estatales**: Tasas por estado de Estados Unidos
- **Impuestos locales**: Tasas por código postal específico
- **Nexus**: Solo calcula impuestos en estados donde hay presencia física
- **Exenciones**: Manejo de clientes y productos exentos

### ✅ **Validación de Tax IDs**
- **EIN (Employer Identification Number)**: Validación completa
- **SSN (Social Security Number)**: Validación con reglas específicas
- **Formateo automático**: Convierte a formato estándar

### ✅ **Integración con Checkout**
- Cálculo automático en el paso 2 del checkout
- Inclusión en PaymentIntent de Stripe
- Desglose detallado para el usuario

## 🏗️ Arquitectura del Sistema

### **TaxService** (`tax_service.py`)
Servicio centralizado que maneja:
- Cálculo de impuestos estatales y locales
- Validación de Tax IDs
- Manejo de exenciones
- Configuración de nexus

### **TaxRoutes** (`tax_routes.py`)
Endpoints REST para:
- Cálculo de impuestos
- Obtención de tasas
- Validación de Tax IDs
- Configuración del sistema

### **Integración con Checkout**
- Cálculo automático en `CheckoutService`
- Inclusión en respuestas del paso 2
- Metadata en PaymentIntent

## 📊 Configuración de Impuestos

### **Estados con Nexus**
```python
nexus_states = ["NJ", "NY", "PA"]
```
Solo se calculan impuestos en estos estados.

### **Tasas Estatales**
```python
state_tax_rates = {
    "NJ": {"rate": 0.06625, "name": "New Jersey"},
    "NY": {"rate": 0.08, "name": "New York"},
    "PA": {"rate": 0.06, "name": "Pennsylvania"},
    # ... más estados
}
```

### **Tasas Locales por Código Postal**
```python
local_tax_rates = {
    "07728": {"rate": 0.0, "name": "Middletown Township"},
    "08527": {"rate": 0.0, "name": "Cranbury Township"},
    # ... más códigos postales
}
```

## 🔧 Endpoints Disponibles

### **Cálculo de Impuestos**
```http
POST /tax/calculate
```

**Request:**
```json
{
  "subtotal": 100.00,
  "shipping_address": {
    "state": "NJ",
    "postcode": "07728",
    "city": "Middletown",
    "address_1": "123 Main St",
    "country": "US"
  },
  "billing_address": {
    "state": "NJ", 
    "postcode": "07728",
    "city": "Middletown",
    "address_1": "123 Main St",
    "country": "US"
  },
  "customer_id": 123
}
```

**Response:**
```json
{
  "subtotal": 100.00,
  "total_tax_rate": 0.06625,
  "total_tax_amount": 6.63,
  "tax_breakdown": {
    "state_tax": {
      "rate": 0.06625,
      "amount": 6.63,
      "name": "New Jersey"
    },
    "local_tax": {
      "rate": 0.0,
      "amount": 0.0,
      "name": "Middletown Township"
    }
  },
  "tax_address": {...},
  "nexus_state": true,
  "calculation_method": "backend_calculation"
}
```

### **Obtener Tasas por Ubicación**
```http
GET /tax/rates/{state}?zip_code={zip}
```

**Response:**
```json
{
  "state": {
    "code": "NJ",
    "rate": 0.06625,
    "name": "New Jersey"
  },
  "local": {
    "zip_code": "07728",
    "rate": 0.0,
    "name": "Middletown Township"
  },
  "total_rate": 0.06625
}
```

### **Validar Tax ID**
```http
POST /tax/validate-tax-id
```

**Request:**
```json
{
  "tax_id": "123456789",
  "country": "US"
}
```

**Response:**
```json
{
  "valid": true,
  "type": "EIN",
  "formatted": "12-3456789",
  "message": "Valid EIN"
}
```

### **Verificar Exención**
```http
POST /tax/check-exempt
```

**Request:**
```json
{
  "customer_id": 123,
  "product_sku": "TAX-FREE-ITEM"
}
```

**Response:**
```json
{
  "is_exempt": true,
  "reason": "Tax exempt customer"
}
```

## 💡 Reglas de Negocio

### **1. Nexus (Presencia Física)**
- Solo se calculan impuestos en estados donde hay presencia física
- Lista configurable de estados con nexus
- Si no hay nexus, no se aplican impuestos

### **2. Dirección para Cálculo**
- Se usa la dirección de envío por defecto
- Si la dirección de facturación es diferente, se usa la de envío
- Esto cumple con las reglas de "origin-based" vs "destination-based"

### **3. Exenciones**
- **Clientes exentos**: Lista de customer IDs
- **Productos exentos**: Lista de SKUs
- **Tax IDs válidos**: Clientes con EIN/SSN válidos pueden ser exentos

### **4. Redondeo**
- Se usa `ROUND_HALF_UP` para cálculos precisos
- Los montos se redondean a 2 decimales
- Compatible con estándares contables

## 🔄 Integración con Checkout

### **Paso 2 del Checkout**
El cálculo de impuestos se integra automáticamente:

1. **Validación de direcciones** (Paso 1)
2. **Cálculo de impuestos** (Paso 2)
3. **Creación de PaymentIntent** con total incluyendo impuestos
4. **Respuesta con desglose** para mostrar al usuario

### **Flujo de Datos**
```
Direcciones → TaxService → Cálculo → PaymentIntent → Respuesta
```

### **Metadata en Stripe**
```json
{
  "app_source": "mobile",
  "customer_email": "user@example.com",
  "step": "2",
  "tax_amount": "6.63"
}
```

## 🧪 Testing y Validación

### **Endpoint de Prueba**
```http
POST /tax/test-calculation
```

**Parámetros:**
- `subtotal`: Monto base
- `state`: Estado para cálculo
- `zip_code`: Código postal

### **Casos de Prueba Comunes**

#### **1. Nueva Jersey (NJ)**
```bash
curl -X POST "http://localhost:8000/tax/test-calculation?subtotal=100&state=NJ&zip_code=07728"
```

#### **2. Estado sin Nexus**
```bash
curl -X POST "http://localhost:8000/tax/test-calculation?subtotal=100&state=CA&zip_code=90210"
```

#### **3. Validación de EIN**
```bash
curl -X POST "http://localhost:8000/tax/validate-tax-id" \
  -H "Content-Type: application/json" \
  -d '{"tax_id": "123456789", "country": "US"}'
```

## 📈 Ventajas sobre el Plugin WordPress

| **Aspecto** | **Plugin WordPress** | **Nuestro Sistema** |
|-------------|----------------------|-------------------|
| **Cálculo** | ❌ Básico, sin nexus | ✅ Completo con nexus |
| **Tasas** | ❌ Hardcodeadas | ✅ Configurables |
| **Exenciones** | ❌ Limitadas | ✅ Flexibles |
| **Tax IDs** | ❌ No validación | ✅ Validación completa |
| **Integración** | ❌ Solo WordPress | ✅ API REST |
| **Escalabilidad** | ❌ Limitada | ✅ Alta |
| **Mantenimiento** | ❌ Difícil | ✅ Fácil |

## 🔮 Próximas Mejoras

### **1. Configuración Dinámica**
- Mover tasas de impuestos a base de datos
- API para actualizar tasas en tiempo real
- Sincronización con servicios externos

### **2. Integración Avanzada**
- Webhooks para cambios en WooCommerce
- Sincronización bidireccional
- Cache de cálculos frecuentes

### **3. Reportes y Analytics**
- Reportes de impuestos por período
- Análisis de exenciones
- Dashboard de configuración

### **4. Compliance**
- Soporte para diferentes países
- Regulaciones específicas por industria
- Auditoría de cálculos

## 🚀 Implementación en Producción

### **Variables de Entorno**
```bash
# Configuración de impuestos
TAX_NEXUS_STATES=NJ,NY,PA
TAX_DEFAULT_RATE=0.06625
TAX_ROUNDING_METHOD=round_half_up

# Configuración de exenciones
TAX_EXEMPT_CUSTOMERS=123,456,789
TAX_EXEMPT_PRODUCTS=TAX-FREE-001,TAX-FREE-002
```

### **Monitoreo**
- Logs de todos los cálculos
- Métricas de tasas de error
- Alertas para cambios en configuración

### **Backup y Recuperación**
- Configuración respaldada en BD
- Versionado de cambios
- Rollback automático

## 📝 Notas de Implementación

1. **Precisión**: Usar `Decimal` para cálculos monetarios
2. **Performance**: Cache de tasas frecuentes
3. **Seguridad**: Validación de entrada estricta
4. **Logging**: Registrar todos los cálculos para auditoría
5. **Testing**: Casos de prueba para todos los estados

---

**¡El sistema de impuestos está completamente implementado y listo para producción!** 🎉
