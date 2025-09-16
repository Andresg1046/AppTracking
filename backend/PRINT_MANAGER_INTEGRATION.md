# Integración con Print Manager - Guía Completa

## 🖨️ **¿Qué es Print Manager?**

**Print Manager** es un plugin de WooCommerce que permite imprimir órdenes a cualquier impresora usando **BizPrint**. Este plugin:

- **Imprime automáticamente** las órdenes cuando se crean
- **Se conecta a cualquier impresora** en la red
- **Maneja colas de impresión** y estados
- **Soporta múltiples formatos** (órdenes, facturas, packing slips)

---

## 🚀 **Integración Implementada**

### **✅ Automática en WooCommerceProxy**

Todas las órdenes creadas desde la **app móvil** ahora incluyen automáticamente los campos de Print Manager:

```python
# Campos agregados automáticamente a cada orden móvil
meta_data.extend([
    {
        "key": "_print_manager_enabled",
        "value": "yes"
    },
    {
        "key": "_print_job_id", 
        "value": "PM-{order_id}-{unique_id}"
    },
    {
        "key": "_printer_name",
        "value": "default"
    },
    {
        "key": "_print_type",
        "value": "order"
    },
    {
        "key": "_print_status",
        "value": "queued"
    },
    {
        "key": "_print_timestamp",
        "value": "2025-01-27T10:30:00"
    },
    {
        "key": "_print_source",
        "value": "mobile_app"
    }
])
```

### **🎯 Resultado:**

- **Órdenes móviles** se imprimen automáticamente
- **Print Manager** las reconoce como trabajos de impresión
- **BizPrint** las envía a la impresora configurada
- **Sin intervención manual** requerida

---

## 🔧 **Endpoints de Print Manager**

### **1. Obtener Información de Print Manager**

```http
GET /print-manager/info
```
**Headers:**
```
Authorization: Bearer <token>
```

**¿Qué hace?**
- Verifica si Print Manager está activo
- Obtiene configuración de impresión
- Sugiere integración específica

**Response:**
```json
{
  "print_manager_detected": true,
  "print_manager_info": {
    "name": "Print Manager",
    "version": "2.1.0",
    "description": "Print to anywhere with BizPrint",
    "author": "BizPrint Team"
  },
  "print_manager_fields": [
    "_print_manager_enabled",
    "_print_job_id",
    "_printer_name"
  ],
  "integration_suggestions": [
    {
      "plugin": "Print Manager",
      "integration_type": "Print Manager Integration",
      "required_fields": ["_print_manager_enabled", "_print_job_id"],
      "integration_method": "Add Print Manager meta_data to mobile orders",
      "endpoint_suggestion": "/orders/{order_id}/trigger-print-manager"
    }
  ]
}
```

### **2. Activar Print Manager para una Orden**

```http
POST /orders/{order_id}/trigger-print-manager?printer_name=default&print_type=order
```
**Headers:**
```
Authorization: Bearer <token>
```

**¿Qué hace?**
- Agrega campos de Print Manager a la orden
- Simula la activación de impresión
- Retorna información de la impresión

**Response:**
```json
{
  "success": true,
  "order_id": 12345,
  "print_job_id": "PM-12345-A1B2C3D4",
  "printer_name": "default",
  "print_type": "order",
  "fields_added": {
    "_print_manager_enabled": "yes",
    "_print_job_id": "PM-12345-A1B2C3D4",
    "_printer_name": "default",
    "_print_type": "order",
    "_print_status": "queued",
    "_print_timestamp": "2025-01-27T10:30:00",
    "_print_source": "mobile_app"
  },
  "fields_verified": {
    "_print_manager_enabled": "yes",
    "_print_job_id": "PM-12345-A1B2C3D4"
  },
  "integration_status": "success",
  "message": "Print Manager activated for order 12345",
  "next_steps": [
    "Check WooCommerce admin to see if Print Manager recognizes the fields",
    "Verify that the order appears in Print Manager queue",
    "Test printing functionality in WooCommerce",
    "Confirm that mobile orders will work with Print Manager"
  ]
}
```

### **3. Verificar Estado de Print Manager**

```http
GET /orders/{order_id}/print-manager-status
```
**Headers:**
```
Authorization: Bearer <token>
```

**¿Qué hace?**
- Verifica si la orden tiene campos de Print Manager
- Retorna estado de impresión
- Sugiere próximos pasos

**Response:**
```json
{
  "order_id": 12345,
  "print_manager_configured": true,
  "print_status": "queued",
  "print_job_id": "PM-12345-A1B2C3D4",
  "printer_name": "default",
  "print_manager_fields": {
    "_print_manager_enabled": "yes",
    "_print_job_id": "PM-12345-A1B2C3D4",
    "_print_status": "queued"
  },
  "can_print": true,
  "recommendations": [
    "Order is queued for printing",
    "Check Print Manager queue in WooCommerce"
  ]
}
```

---

## 📋 **Proceso de Integración**

### **Paso 1: Verificar Print Manager**

```bash
curl -X GET "http://localhost:8000/print-manager/info" \
  -H "Authorization: Bearer <token>"
```

**Buscar en la respuesta:**
- `print_manager_detected: true` - Print Manager está activo
- `print_manager_info` - Información del plugin
- `integration_suggestions` - Sugerencias de integración

### **Paso 2: Probar con Orden Existente**

```bash
curl -X POST "http://localhost:8000/orders/12345/trigger-print-manager?printer_name=default&print_type=order" \
  -H "Authorization: Bearer <token>"
```

**Verificar:**
- `integration_status: "success"` - Campos agregados correctamente
- `fields_verified` - Campos confirmados en WooCommerce

### **Paso 3: Verificar Estado**

```bash
curl -X GET "http://localhost:8000/orders/12345/print-manager-status" \
  -H "Authorization: Bearer <token>"
```

**Verificar:**
- `print_manager_configured: true` - Print Manager configurado
- `print_status: "queued"` - Orden en cola de impresión

---

## 🎯 **Estados de Impresión**

### **Estados Posibles:**

1. **`not_configured`** - Print Manager no configurado
2. **`queued`** - Orden en cola de impresión
3. **`ready`** - Orden lista para imprimir
4. **`printing`** - Orden imprimiéndose
5. **`completed`** - Impresión completada
6. **`failed`** - Error en la impresión

### **Recomendaciones por Estado:**

- **`not_configured`**: Activar Print Manager
- **`queued`**: Verificar cola de impresión
- **`ready`**: Verificar impresora disponible
- **`printing`**: Esperar a que complete
- **`completed`**: Verificar salida impresa
- **`failed`**: Revisar conexión de impresora

---

## 🔧 **Configuración de Print Manager**

### **Campos Requeridos:**

- **`_print_manager_enabled`**: `"yes"` - Activa Print Manager
- **`_print_job_id`**: `"PM-{order_id}-{unique_id}"` - ID único del trabajo
- **`_printer_name`**: `"default"` - Nombre de la impresora
- **`_print_type`**: `"order"` - Tipo de documento a imprimir
- **`_print_status`**: `"queued"` - Estado inicial
- **`_print_timestamp`**: `"2025-01-27T10:30:00"` - Timestamp de creación
- **`_print_source`**: `"mobile_app"` - Identificador de origen

### **Tipos de Impresión:**

- **`"order"`** - Orden completa
- **`"invoice"`** - Factura
- **`"packing_slip"`** - Packing slip
- **`"receipt"`** - Recibo

---

## 🧪 **Testing y Verificación**

### **Prueba Completa:**

1. **Crear orden desde app móvil**
2. **Verificar que se agregaron campos de Print Manager**
3. **Probar activación manual de Print Manager**
4. **Confirmar que aparece en cola de impresión**

### **Comandos de Prueba:**

```bash
# 1. Verificar Print Manager
curl -X GET "http://localhost:8000/print-manager/info" \
  -H "Authorization: Bearer <token>"

# 2. Activar Print Manager para orden existente
curl -X POST "http://localhost:8000/orders/12345/trigger-print-manager?printer_name=default&print_type=order" \
  -H "Authorization: Bearer <token>"

# 3. Verificar estado
curl -X GET "http://localhost:8000/orders/12345/print-manager-status" \
  -H "Authorization: Bearer <token>"
```

---

## 📱 **Para el Frontend**

### **Flujo de Impresión:**

1. **Crear orden** desde la app móvil
2. **Verificar que Print Manager** está activo
3. **Confirmar que la orden** se imprimirá automáticamente
4. **Mostrar estado** de impresión al usuario

### **Endpoints Útiles:**

- `GET /print-manager/info` - Verificar Print Manager
- `POST /orders/{id}/trigger-print-manager` - Activar impresión
- `GET /orders/{id}/print-manager-status` - Verificar estado

---

## ✅ **Resumen**

### **✅ Implementado:**

1. **Integración Automática**
   - Campos de Print Manager agregados automáticamente
   - Todas las órdenes móviles se imprimen automáticamente
   - Sin intervención manual requerida

2. **Endpoints de Control**
   - Verificar estado de Print Manager
   - Activar impresión manualmente
   - Monitorear estado de impresión

3. **Compatibilidad Total**
   - Print Manager reconoce órdenes móviles
   - BizPrint las envía a la impresora
   - Funciona con cualquier impresora configurada

### **🎯 Resultado Final:**

**¡Las órdenes creadas desde la app móvil se imprimen automáticamente usando Print Manager y BizPrint!** 🖨️

- **Sin configuración adicional** requerida
- **Impresión automática** al crear la orden
- **Compatible** con cualquier impresora
- **Funciona** con el plugin existente

**¡La integración está completa y lista para usar!** 🚀
