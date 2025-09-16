# Sistema de Envío - Documentación Completa

## 🚚 Visión General

El sistema de envío implementado maneja completamente el cálculo de costos de envío, métodos disponibles, y fechas de entrega, reemplazando la funcionalidad básica del plugin WordPress.

## 🎯 Características Principales

### ✅ **Métodos de Envío Configurables**
- **Flat Rate**: Envío estándar ($10.00)
- **Local Pickup**: Recogida en tienda (gratis)
- **Express Delivery**: Entrega el mismo día ($25.00)
- **Premium Delivery**: Envío premium con tracking ($20.00)

### ✅ **Cálculo Inteligente**
- **Envío gratis** sobre umbral configurable ($75.00)
- **Validación por código postal** (solo códigos válidos)
- **Cálculo de fechas** basado en días hábiles
- **Cutoff time** para entregas el mismo día (3:00 PM)

### ✅ **Integración con Impuestos**
- Los envíos están sujetos a impuestos
- Cálculo correcto: Subtotal + Envío = Base para impuestos
- Compatible con el sistema de impuestos implementado

## 🏗️ Arquitectura del Sistema

### **ShippingService** (`shipping_service.py`)
Servicio centralizado que maneja:
- Cálculo de costos de envío
- Validación de métodos por código postal
- Cálculo de fechas de entrega
- Manejo de envío gratis

### **ShippingRoutes** (`shipping_routes.py`)
Endpoints REST para:
- Cálculo de opciones de envío
- Obtención de métodos disponibles
- Validación de métodos
- Configuración del sistema

### **Integración con Checkout**
- Cálculo automático en `CheckoutService`
- Inclusión en respuestas del paso 2
- Compatibilidad con cálculo de impuestos

## 📊 Configuración de Envío

### **Métodos Disponibles**
```python
shipping_methods = {
    "flat_rate": {
        "title": "Delivery Service",
        "cost": 10.00,
        "free_shipping_threshold": 75.00,
        "delivery_days": 1
    },
    "local_pickup": {
        "title": "Store Pickup", 
        "cost": 0.00,
        "delivery_days": 0
    },
    "express_delivery": {
        "title": "Express Delivery",
        "cost": 25.00,
        "delivery_days": 0,
        "cutoff_time": 15  # 3:00 PM
    },
    "premium_delivery": {
        "title": "Premium Delivery",
        "cost": 20.00,
        "delivery_days": 1
    }
}
```

### **Configuración General**
```python
shipping_config = {
    "default_method": "flat_rate",
    "free_shipping_enabled": True,
    "free_shipping_threshold": 75.00,
    "tax_shipping": True,  # Los envíos están sujetos a impuestos
    "delivery_cutoff_time": 15,  # 3:00 PM
    "business_days_only": True,
    "weekend_delivery": False
}
```

## 🔧 Endpoints Disponibles

### **Calcular Opciones de Envío**
```http
POST /shipping/calculate
```

**Request:**
```json
{
  "zip_code": "07728",
  "cart_total": 54.99,
  "selected_method": "flat_rate",
  "delivery_date": "2025-09-10"
}
```

**Response:**
```json
{
  "available_methods": [
    {
      "id": "flat_rate",
      "title": "Delivery Service",
      "description": "Standard delivery service",
      "cost": 10.00,
      "free": false,
      "delivery_days": 1,
      "delivery_date": "Wednesday, September 11, 2025",
      "delivery_time": "1 business day(s)",
      "available": true
    }
  ],
  "selected_method": {...},
  "valid_zip": true
}
```

### **Calcular Total con Envío**
```http
POST /shipping/total
```

**Request:**
```json
{
  "subtotal": 54.99,
  "shipping_method_id": "flat_rate",
  "zip_code": "07728",
  "cart_total": 54.99
}
```

**Response:**
```json
{
  "subtotal": 54.99,
  "shipping_cost": 10.00,
  "shipping_method": {...},
  "total_before_tax": 64.99,
  "shipping_taxable": true
}
```

### **Obtener Métodos Disponibles**
```http
GET /shipping/methods
```

**Response:**
```json
[
  {
    "id": "flat_rate",
    "title": "Delivery Service",
    "description": "Standard delivery service",
    "cost": 10.00,
    "free": false,
    "delivery_days": 1,
    "delivery_date": "",
    "delivery_time": "",
    "available": true
  }
]
```

### **Validar Método de Envío**
```http
POST /shipping/validate-method
```

**Request:**
```json
{
  "method_id": "flat_rate",
  "zip_code": "07728"
}
```

**Response:**
```json
{
  "valid": true,
  "message": "Valid",
  "method_id": "flat_rate",
  "zip_code": "07728"
}
```

## 💡 Reglas de Negocio

### **1. Validación por Código Postal**
- Solo códigos postales válidos pueden recibir envíos
- Lista configurable de códigos postales válidos
- Validación automática en todos los cálculos

### **2. Envío Gratis**
- Se aplica automáticamente sobre el umbral configurado
- Umbral por método de envío (configurable)
- Cálculo dinámico basado en total del carrito

### **3. Cálculo de Fechas**
- **Local Pickup**: Mismo día
- **Express Delivery**: Mismo día (antes de 3:00 PM)
- **Métodos estándar**: 1+ días hábiles
- **Fines de semana**: No disponibles (configurable)

### **4. Integración con Impuestos**
- Los envíos están sujetos a impuestos
- Base para impuestos = Subtotal + Envío
- Compatible con sistema de nexus

## 🔄 Flujo de Cálculo Completo

### **En el Checkout (Paso 2):**

1. **Usuario selecciona método de envío**
2. **Sistema calcula costo de envío**
3. **Sistema calcula total antes de impuestos** (Subtotal + Envío)
4. **Sistema calcula impuestos** sobre el total
5. **Sistema crea PaymentIntent** con total final
6. **Usuario ve desglose completo**

### **Ejemplo de Cálculo:**

```
Subtotal: $54.99
Envío: $10.00 (Delivery Service)
Total antes de impuestos: $64.99
Impuestos (6.625%): $4.30
Total final: $69.29
```

## 🧪 Testing y Validación

### **Endpoint de Prueba**
```http
POST /shipping/test-calculation
```

**Parámetros:**
- `zip_code`: Código postal
- `cart_total`: Total del carrito
- `method_id`: Método de envío

### **Casos de Prueba Comunes**

#### **1. Envío Estándar**
```bash
curl -X POST "http://localhost:8000/shipping/test-calculation?zip_code=07728&cart_total=54.99&method_id=flat_rate"
```

#### **2. Envío Gratis**
```bash
curl -X POST "http://localhost:8000/shipping/test-calculation?zip_code=07728&cart_total=75.00&method_id=flat_rate"
```

#### **3. Código Postal Inválido**
```bash
curl -X POST "http://localhost:8000/shipping/test-calculation?zip_code=99999&cart_total=54.99&method_id=flat_rate"
```

## 📈 Ventajas sobre el Plugin WordPress

| **Aspecto** | **Plugin WordPress** | **Nuestro Sistema** |
|-------------|----------------------|-------------------|
| **Métodos** | ❌ Limitados | ✅ Configurables |
| **Envío Gratis** | ❌ Básico | ✅ Por umbral |
| **Fechas** | ❌ Estáticas | ✅ Dinámicas |
| **Validación** | ❌ Limitada | ✅ Por código postal |
| **Integración** | ❌ Solo WordPress | ✅ API REST |
| **Impuestos** | ❌ Separado | ✅ Integrado |

## 🔮 Próximas Mejoras

### **1. Métodos Dinámicos**
- Integración con APIs de transportistas
- Cálculo en tiempo real de costos
- Tracking automático

### **2. Configuración Avanzada**
- Métodos por región
- Costos por peso/volumen
- Descuentos por volumen

### **3. Analytics**
- Reportes de envío
- Métricas de costos
- Optimización de rutas

## 🚀 Implementación en Producción

### **Variables de Entorno**
```bash
# Configuración de envío
SHIPPING_DEFAULT_METHOD=flat_rate
SHIPPING_FREE_THRESHOLD=75.00
SHIPPING_CUTOFF_TIME=15
SHIPPING_TAXABLE=true
```

### **Monitoreo**
- Logs de todos los cálculos
- Métricas de métodos populares
- Alertas para códigos postales inválidos

## 📝 Notas de Implementación

1. **Precisión**: Usar `Decimal` para cálculos monetarios
2. **Performance**: Cache de métodos frecuentes
3. **Validación**: Verificar códigos postales en cada cálculo
4. **Logging**: Registrar todos los cálculos para auditoría
5. **Testing**: Casos de prueba para todos los métodos

## 🔗 Integración con Otros Sistemas

### **Con Sistema de Impuestos**
- Envío incluido en base de impuestos
- Cálculo correcto de totales
- Compatibilidad con nexus

### **Con Sistema de Validación**
- Mismos códigos postales válidos
- Validación consistente
- Manejo de errores unificado

### **Con Checkout**
- Cálculo automático en paso 2
- Información completa en respuesta
- Compatibilidad con PaymentIntent

---

**¡El sistema de envío está completamente implementado y es mucho más robusto que el plugin WordPress!** 🎉

## 📱 Para la App Móvil

Ahora tu app puede:

1. **Calcular envío** en tiempo real por código postal
2. **Mostrar métodos disponibles** con costos y fechas
3. **Aplicar envío gratis** automáticamente
4. **Integrar con impuestos** correctamente
5. **Validar métodos** por ubicación
6. **Mostrar fechas de entrega** precisas

El sistema maneja completamente el flujo de envío que viste en la imagen, con cálculos precisos y validaciones robustas.
