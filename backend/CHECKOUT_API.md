# API de Checkout Multi-Paso

Este documento describe la nueva API de checkout que reemplaza la funcionalidad del plugin WordPress "Woocommerce Checkout Page" por Ansar A.

## 🎯 Objetivo

Centralizar toda la lógica de checkout en el backend FastAPI, eliminando la dependencia del plugin WordPress y proporcionando una API robusta y escalable para la aplicación móvil.

## 🏗️ Arquitectura

### Componentes Principales

1. **ValidationService** (`validation_service.py`)
   - Validación de códigos postales
   - Validación de campos de checkout
   - Cálculo de fechas de entrega
   - Configuración de entregas

2. **CheckoutService** (`checkout_service.py`)
   - Lógica de checkout multi-paso
   - Integración con Stripe
   - Creación de órdenes en WooCommerce

3. **CheckoutRoutes** (`checkout_routes.py`)
   - Endpoints REST para checkout
   - Validaciones individuales
   - Procesamiento por pasos

## 📋 Flujo de Checkout

### Paso 1: Información de Envío
```http
POST /checkout/step1
```

**Campos requeridos:**
- `shipping_first_name`
- `shipping_last_name`
- `shipping_address_1`
- `shipping_city`
- `shipping_state`
- `shipping_postcode`
- `use_for_storepickup` (boolean)

**Validaciones:**
- Código postal válido (lista hardcodeada)
- Campos requeridos completos
- Información de ubicación desde API externa

**Respuesta:**
```json
{
  "is_valid": true,
  "errors": [],
  "location_info": {
    "city": "New York",
    "state": "NY",
    "state_name": "New York",
    "country": "United States"
  },
  "delivery_date": "Monday, December 16, 2024",
  "hidden_delivery_date": "16-12-2024",
  "available_delivery_dates": [...]
}
```

### Paso 2: Información de Facturación y Pago
```http
POST /checkout/step2
```

**Campos requeridos:**
- `billing_first_name`
- `billing_last_name`
- `billing_address_1`
- `billing_city`
- `billing_state`
- `billing_postcode`
- `billing_email`
- `billing_phone`
- `payment_method`

**Validaciones:**
- Campos de facturación completos
- Email válido
- Método de pago válido
- Creación de PaymentIntent en Stripe

**Respuesta:**
```json
{
  "is_valid": true,
  "errors": [],
  "payment_intent": {
    "client_secret": "pi_xxx_secret_xxx",
    "payment_intent_id": "pi_xxx",
    "amount": 50.00,
    "currency": "usd",
    "status": "requires_payment_method"
  }
}
```

### Paso 3: Creación de Orden
```http
POST /checkout/step3
```

**Campos requeridos:**
- `cart_items` (lista de productos)
- `shipping_lines` (opcional)
- `coupon_lines` (opcional)
- `final_confirmation` (boolean)

**Proceso:**
- Crear orden en WooCommerce
- Configurar tracking
- Retornar información de la orden

**Respuesta:**
```json
{
  "order": {
    "id": 12345,
    "status": "pending",
    "currency": "USD",
    "total": "50.00",
    "payment_method": "stripe_cc",
    "billing": {...},
    "shipping": {...},
    "line_items": [...],
    "tracking_info": null
  },
  "payment_status": "pending",
  "tracking_info": null
}
```

## 🔧 Endpoints de Utilidad

### Validación de Código Postal
```http
POST /checkout/validate-zip
```

### Fechas de Entrega Disponibles
```http
POST /checkout/delivery-dates
```

### Configuración de Entregas
```http
GET /checkout/delivery-config
```

### Método de Pago por Defecto
```http
GET /checkout/default-payment-method
```

## 💳 Integración con Stripe

### Crear PaymentIntent
```http
POST /ecommerce/create-payment-intent
```

**Parámetros:**
- `amount`: Monto en dólares
- `currency`: Moneda (default: "usd")
- `customer_email`: Email del cliente (opcional)
- `order_id`: ID de la orden (opcional)

### Confirmar Pago
```http
POST /ecommerce/confirm-payment-intent
```

**Parámetros:**
- `payment_intent_id`: ID del PaymentIntent
- `order_id`: ID de la orden

## 🚚 Configuración de Entregas

### Códigos Postales Válidos
Lista hardcodeada de códigos postales válidos para entrega:
```python
valid_zip_codes = [
    "07728", "08527", "07731", "07727", "07722", "07746", "07738", 
    "08701", "07721", "07747", "08879", "08857", "07751", "07733", 
    # ... más códigos
]
```

### Configuración de Entregas
- **Hora límite**: 3:00 PM (15:00)
- **Días de entrega**: Lunes a Sábado (no domingos)
- **API de ubicación**: Zippopotam.us para obtener ciudad/estado

## 🔄 Migración desde Plugin WordPress

### Funcionalidades Reemplazadas

1. **Validación de códigos postales**
   - ❌ Plugin: JavaScript hardcodeado
   - ✅ Backend: Servicio centralizado con API externa

2. **Checkout multi-paso**
   - ❌ Plugin: Lógica en JavaScript
   - ✅ Backend: API REST estructurada

3. **Integración con Stripe**
   - ❌ Plugin: Configuración básica
   - ✅ Backend: PaymentIntents con metadata

4. **Cálculo de fechas de entrega**
   - ❌ Plugin: Lógica compleja en PHP
   - ✅ Backend: Servicio dedicado

5. **Validación de campos**
   - ❌ Plugin: Validación distribuida
   - ✅ Backend: Validación centralizada

### Beneficios de la Migración

1. **Centralización**: Toda la lógica en el backend
2. **Escalabilidad**: API REST estándar
3. **Mantenibilidad**: Código organizado y documentado
4. **Seguridad**: Validaciones en el servidor
5. **Flexibilidad**: Fácil modificación de reglas de negocio

## 🧪 Testing

### Ejemplo de Flujo Completo

```python
# Paso 1: Validar envío
step1_response = await client.post("/checkout/step1", json={
    "shipping_first_name": "John",
    "shipping_last_name": "Doe",
    "shipping_address_1": "123 Main St",
    "shipping_city": "New York",
    "shipping_state": "NY",
    "shipping_postcode": "10001",
    "use_for_storepickup": False
})

# Paso 2: Configurar pago
step2_response = await client.post("/checkout/step2", json={
    "billing_first_name": "John",
    "billing_last_name": "Doe",
    "billing_address_1": "123 Main St",
    "billing_city": "New York",
    "billing_state": "NY",
    "billing_postcode": "10001",
    "billing_email": "john@example.com",
    "billing_phone": "555-1234",
    "payment_method": "stripe_cc"
})

# Paso 3: Crear orden
step3_response = await client.post("/checkout/step3", json={
    "cart_items": [
        {
            "product_id": 123,
            "quantity": 1,
            "price": "25.00"
        }
    ],
    "final_confirmation": True
})
```

## 📝 Notas de Implementación

1. **Configuración de Stripe**: Variables de entorno requeridas
2. **Códigos postales**: Lista hardcodeada (considerar mover a BD)
3. **API externa**: Zippopotam.us para información de ubicación
4. **Logging**: Todos los errores se registran para debugging
5. **Rate limiting**: Aplicado a todos los endpoints

## 🔮 Próximos Pasos

1. **Configuración dinámica**: Mover códigos postales a base de datos
2. **Cache**: Implementar cache para validaciones frecuentes
3. **Webhooks**: Mejorar manejo de webhooks de Stripe
4. **Testing**: Agregar tests unitarios y de integración
5. **Documentación**: Swagger/OpenAPI automática
