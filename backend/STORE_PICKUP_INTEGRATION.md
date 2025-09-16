# Store Pickup & WooCommerce Integration - Documentación Completa

## 🏪 **Store Pickup - Funcionalidad Implementada**

### **¿Qué es Store Pickup?**
Store Pickup permite a los clientes recoger sus pedidos directamente en la tienda física, eliminando costos de envío y tiempos de entrega.

### **Validaciones Específicas para Store Pickup**

#### **Campos Requeridos (Mínimos)**
- ✅ `billing_first_name` - Nombre
- ✅ `billing_last_name` - Apellido  
- ✅ `billing_email` - Email
- ✅ `billing_phone` - Teléfono

#### **Campos Opcionales**
- `billing_address_1` - Dirección (opcional)
- `billing_city` - Ciudad (opcional)
- `billing_state` - Estado (opcional)
- `billing_postcode` - Código postal (opcional)

#### **Campos NO Requeridos**
- ❌ `shipping_first_name` - No necesario
- ❌ `shipping_address_1` - No necesario
- ❌ `shipping_postcode` - No necesario
- ❌ Validación de código postal - No aplica

---

## 🚀 **Endpoints Específicos para Store Pickup**

### **1. Calcular Store Pickup**
```http
POST /shipping/store-pickup/calculate
```
**Request:**
```json
{
  "cart_total": 54.99
}
```
**Response:**
```json
{
  "available_methods": [
    {
      "id": "local_pickup",
      "title": "Store Pickup",
      "description": "Pick up at our store location",
      "cost": 0.00,
      "free": true,
      "delivery_days": 0,
      "delivery_date": "Monday, January 27, 2025",
      "delivery_time": "Same day pickup",
      "available": true
    }
  ],
  "selected_method": {...},
  "valid_zip": true,
  "is_store_pickup": true
}
```

### **2. Validar Información de Store Pickup**
```http
POST /shipping/store-pickup/validate
```
**Request:**
```json
{
  "billing_first_name": "John",
  "billing_last_name": "Doe",
  "billing_email": "john@example.com",
  "billing_phone": "555-1234"
}
```
**Response:**
```json
{
  "is_valid": true,
  "errors": [],
  "required_fields": ["billing_first_name", "billing_last_name", "billing_email", "billing_phone"],
  "optional_fields": ["billing_address_1", "billing_city", "billing_state", "billing_postcode"]
}
```

### **3. Obtener Información de la Tienda**
```http
GET /shipping/store-pickup/info
```
**Response:**
```json
{
  "store_name": "Flowers Freehold",
  "store_address": {
    "street": "123 Main Street",
    "city": "Freehold",
    "state": "NJ",
    "zip_code": "07728",
    "country": "US"
  },
  "business_hours": {
    "monday": "9:00 AM - 6:00 PM",
    "tuesday": "9:00 AM - 6:00 PM",
    "wednesday": "9:00 AM - 6:00 PM",
    "thursday": "9:00 AM - 6:00 PM",
    "friday": "9:00 AM - 7:00 PM",
    "saturday": "9:00 AM - 5:00 PM",
    "sunday": "Closed"
  },
  "pickup_instructions": [
    "Presentar identificación válida",
    "Mostrar confirmación de orden en el teléfono",
    "Recoger dentro de 7 días hábiles",
    "Contactar tienda si necesita más tiempo"
  ],
  "contact_info": {
    "phone": "(555) 123-4567",
    "email": "info@flowersfreehold.com"
  },
  "pickup_method": {...}
}
```

---

## 🛒 **Checkout con Store Pickup**

### **Paso 1: Información de Envío**
```http
POST /checkout/step1
```
**Request (Store Pickup):**
```json
{
  "shipping_first_name": "John",
  "shipping_last_name": "Doe",
  "shipping_address_1": "",
  "shipping_city": "",
  "shipping_state": "",
  "shipping_postcode": "",
  "shipping_country": "US",
  "shipping_phone": "",
  "use_for_storepickup": true,
  "use_for_billing": true,
  "delivery_date": null,
  "message_card": "Happy Birthday!",
  "delivery_instructions": ""
}
```
**Response:**
```json
{
  "is_valid": true,
  "errors": [],
  "location_info": {
    "city": "Store Location",
    "state": "NJ",
    "state_name": "New Jersey",
    "country": "United States"
  },
  "delivery_date": null,
  "hidden_delivery_date": null,
  "available_delivery_dates": []
}
```

### **Paso 2: Información de Facturación**
```http
POST /checkout/step2
```
**Request (Store Pickup):**
```json
{
  "billing_first_name": "John",
  "billing_last_name": "Doe",
  "billing_address_1": "123 Main St",
  "billing_address_2": "",
  "billing_city": "Freehold",
  "billing_state": "NJ",
  "billing_postcode": "07728",
  "billing_country": "US",
  "billing_email": "john@example.com",
  "billing_phone": "555-1234",
  "payment_method": "stripe_cc",
  "payment_method_title": "Credit Card (Stripe)"
}
```
**Response:**
```json
{
  "is_valid": true,
  "errors": [],
  "payment_intent": {...},
  "tax_calculation": {...},
  "shipping_calculation": {
    "subtotal": 54.99,
    "shipping_cost": 0.00,
    "shipping_method": {
      "id": "local_pickup",
      "title": "Store Pickup",
      "cost": 0.00,
      "free": true
    },
    "total_before_tax": 54.99,
    "shipping_taxable": true
  }
}
```

---

## 🏪 **Integración con WooCommerce**

### **Meta Data Agregada Automáticamente**

Cada orden creada desde la app móvil incluye estos campos en WooCommerce:

```json
{
  "meta_data": [
    {
      "key": "_app_source",
      "value": "mobile_app"
    },
    {
      "key": "_app_version", 
      "value": "1.0"
    },
    {
      "key": "_created_via",
      "value": "mobile_checkout"
    },
    {
      "key": "_store_pickup",
      "value": "yes"
    },
    {
      "key": "_delivery_date",
      "value": "2025-01-27"
    },
    {
      "key": "_message_card",
      "value": "Happy Birthday!"
    },
    {
      "key": "_delivery_instructions",
      "value": "Leave at front door"
    },
    {
      "key": "_location_type",
      "value": "store"
    }
  ]
}
```

### **Datos de Envío para Store Pickup**

Para órdenes de Store Pickup, los datos de envío se generan automáticamente:

```json
{
  "shipping": {
    "first_name": "John (PICKUP)",
    "last_name": "Doe (PICKUP)",
    "company": "",
    "address_1": "123 Main St",
    "address_2": "",
    "city": "Freehold",
    "state": "NJ",
    "postcode": "07728",
    "country": "US",
    "phone": "555-1234"
  }
}
```

### **Customer Note Automática**

```json
{
  "customer_note": "Orden creada desde app móvil - Store Pickup"
}
```

---

## 🔍 **Verificación de Órdenes**

### **Verificar Orden Específica**
```http
GET /orders/{order_id}/verify
```
**Headers:**
```
Authorization: Bearer <token>
```
**Response:**
```json
{
  "order_exists": true,
  "order_id": 12345,
  "order_summary": {...},
  "woocommerce_details": {
    "raw_data": {...},
    "meta_data": [...],
    "line_items": [...],
    "shipping_lines": [...],
    "tax_lines": [...],
    "customer_note": "Orden creada desde app móvil - Store Pickup"
  },
  "plugin_compatibility": {
    "has_app_source": true,
    "has_store_pickup": true,
    "has_delivery_date": true,
    "has_message_card": true
  }
}
```

### **Ver Órdenes Recientes**
```http
GET /orders/recent?limit=10
```
**Headers:**
```
Authorization: Bearer <token>
```
**Response:**
```json
{
  "total_recent_orders": 10,
  "mobile_orders": [
    {
      "id": 12345,
      "status": "pending",
      "total": "54.99",
      "payment_method": "stripe_cc",
      "date_created": "2025-01-27T10:30:00Z",
      "customer_note": "Orden creada desde app móvil - Store Pickup",
      "is_store_pickup": true,
      "delivery_date": "2025-01-27"
    }
  ],
  "mobile_orders_count": 1,
  "all_recent_orders": [...]
}
```

---

## 🖨️ **Compatibilidad con Plugin de Impresión**

### **Campos Esenciales para Impresión**

Las órdenes creadas desde la app móvil incluyen todos los campos necesarios para plugins de impresión automática:

#### **Información Básica**
- ✅ `id` - ID de la orden
- ✅ `status` - Estado de la orden
- ✅ `total` - Total de la orden
- ✅ `payment_method` - Método de pago
- ✅ `date_created` - Fecha de creación

#### **Información de Cliente**
- ✅ `billing` - Datos de facturación completos
- ✅ `shipping` - Datos de envío (o pickup)
- ✅ `customer_note` - Nota del cliente

#### **Productos y Servicios**
- ✅ `line_items` - Productos de la orden
- ✅ `shipping_lines` - Líneas de envío
- ✅ `tax_lines` - Líneas de impuestos
- ✅ `coupon_lines` - Cupones aplicados

#### **Meta Data Personalizada**
- ✅ `_store_pickup` - Indica si es pickup
- ✅ `_delivery_date` - Fecha de entrega
- ✅ `_message_card` - Mensaje de tarjeta
- ✅ `_delivery_instructions` - Instrucciones de entrega
- ✅ `_app_source` - Origen de la orden

### **Ejemplo de Orden Completa para Impresión**

```json
{
  "id": 12345,
  "status": "pending",
  "currency": "USD",
  "total": "54.99",
  "payment_method": "stripe_cc",
  "payment_method_title": "Credit Card (Stripe)",
  "date_created": "2025-01-27T10:30:00Z",
  "customer_note": "Orden creada desde app móvil - Store Pickup",
  "billing": {
    "first_name": "John",
    "last_name": "Doe",
    "company": "",
    "address_1": "123 Main St",
    "address_2": "",
    "city": "Freehold",
    "state": "NJ",
    "postcode": "07728",
    "country": "US",
    "email": "john@example.com",
    "phone": "555-1234"
  },
  "shipping": {
    "first_name": "John (PICKUP)",
    "last_name": "Doe (PICKUP)",
    "company": "",
    "address_1": "123 Main St",
    "address_2": "",
    "city": "Freehold",
    "state": "NJ",
    "postcode": "07728",
    "country": "US",
    "phone": "555-1234"
  },
  "line_items": [
    {
      "id": 1,
      "name": "Beautiful Rose Bouquet",
      "product_id": 123,
      "variation_id": 0,
      "quantity": 1,
      "subtotal": "54.99",
      "total": "54.99",
      "sku": "ROSE-001"
    }
  ],
  "shipping_lines": [
    {
      "id": 1,
      "method_title": "Store Pickup",
      "method_id": "local_pickup",
      "total": "0.00"
    }
  ],
  "tax_lines": [
    {
      "id": 1,
      "rate_code": "NJ-TAX-1",
      "rate_id": 1,
      "label": "Tax",
      "compound": false,
      "tax_total": "3.64",
      "shipping_tax_total": "0.00"
    }
  ],
  "meta_data": [
    {
      "id": 1,
      "key": "_app_source",
      "value": "mobile_app"
    },
    {
      "id": 2,
      "key": "_store_pickup",
      "value": "yes"
    },
    {
      "id": 3,
      "key": "_message_card",
      "value": "Happy Birthday!"
    }
  ]
}
```

---

## 🧪 **Testing y Debugging**

### **Pruebas Rápidas**

#### **1. Probar Store Pickup**
```bash
curl -X POST "http://localhost:8000/shipping/store-pickup/calculate" \
  -H "Content-Type: application/json" \
  -d '{"cart_total": 54.99}'
```

#### **2. Validar Información de Pickup**
```bash
curl -X POST "http://localhost:8000/shipping/store-pickup/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "billing_first_name": "John",
    "billing_last_name": "Doe", 
    "billing_email": "john@example.com",
    "billing_phone": "555-1234"
  }'
```

#### **3. Obtener Info de la Tienda**
```bash
curl -X GET "http://localhost:8000/shipping/store-pickup/info"
```

#### **4. Verificar Orden en WooCommerce**
```bash
curl -X GET "http://localhost:8000/orders/12345/verify" \
  -H "Authorization: Bearer <token>"
```

#### **5. Ver Órdenes Recientes**
```bash
curl -X GET "http://localhost:8000/orders/recent?limit=5" \
  -H "Authorization: Bearer <token>"
```

---

## 📱 **Para el Frontend**

### **Flujo Recomendado para Store Pickup**

1. **Mostrar Opción de Pickup**
   - `GET /shipping/store-pickup/info` - Obtener info de la tienda
   - Mostrar horarios y ubicación

2. **Validar Información Mínima**
   - `POST /shipping/store-pickup/validate` - Validar datos básicos
   - Solo requerir: nombre, apellido, email, teléfono

3. **Calcular Costos**
   - `POST /shipping/store-pickup/calculate` - Calcular (siempre $0)
   - `POST /tax/calculate` - Calcular impuestos

4. **Procesar Checkout**
   - `POST /checkout/step1` con `use_for_storepickup: true`
   - `POST /checkout/step2` con datos de facturación
   - `POST /checkout/step3` para crear orden

5. **Verificar Orden**
   - `GET /orders/{order_id}/verify` - Confirmar que se creó correctamente

### **Diferencias en la UI**

#### **Para Envío Normal:**
- ✅ Campos de dirección de envío requeridos
- ✅ Validación de código postal
- ✅ Selección de método de envío
- ✅ Cálculo de costos de envío

#### **Para Store Pickup:**
- ❌ Campos de dirección de envío opcionales
- ❌ Sin validación de código postal
- ✅ Solo método "Store Pickup" disponible
- ✅ Costo de envío siempre $0.00
- ✅ Información de la tienda visible

---

## ✅ **Resumen de Implementación**

### **✅ Completado:**

1. **Validación Store Pickup**
   - Campos mínimos requeridos
   - Sin validación de código postal
   - Lógica diferenciada en ValidationService

2. **Cálculo de Envío**
   - Método `local_pickup` siempre disponible
   - Costo siempre $0.00
   - Exclusión de otros métodos cuando es pickup

3. **Integración WooCommerce**
   - Meta data completa para plugins
   - Datos de envío generados automáticamente
   - Customer note identificando origen móvil

4. **Endpoints Específicos**
   - `/shipping/store-pickup/calculate`
   - `/shipping/store-pickup/validate`
   - `/shipping/store-pickup/info`

5. **Verificación de Órdenes**
   - `/orders/{order_id}/verify`
   - `/orders/recent`
   - Compatibilidad con plugins de impresión

### **🎯 Beneficios:**

- ✅ **Plugin de Impresión Funciona**: Todas las órdenes se guardan con estructura completa
- ✅ **Store Pickup Simplificado**: Solo campos esenciales requeridos
- ✅ **Debugging Fácil**: Endpoints para verificar órdenes
- ✅ **Compatibilidad Total**: Meta data para todos los plugins de WooCommerce
- ✅ **UX Mejorada**: Flujo diferenciado para pickup vs envío

**¡El sistema está listo para producción!** 🚀
