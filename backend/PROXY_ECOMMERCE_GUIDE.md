# 🛒 Guía E-commerce Proxy - Solo Interfaz para WooCommerce

## 🎯 **Enfoque: Solo Proxy/Puente**

Esta implementación actúa como **solo una interfaz** entre tu app móvil y WooCommerce. **No hay datos locales** de carrito, órdenes, etc. Todo se maneja directamente en WordPress/WooCommerce.

## 🚀 **Endpoints Disponibles**

### 1. **Productos** (Directo desde WooCommerce)
- `GET /ecommerce/products` - Listar productos
- `GET /ecommerce/products/{id}` - Obtener producto específico
- `GET /ecommerce/categories` - Obtener categorías

### 2. **Carrito** (Solo cálculo, no persistencia)
- `POST /ecommerce/cart/calculate` - Calcular totales del carrito

### 3. **Órdenes** (Directo en WooCommerce)
- `POST /ecommerce/orders` - Crear orden en WooCommerce
- `GET /ecommerce/orders` - Listar órdenes del cliente
- `GET /ecommerce/orders/{id}` - Obtener orden específica
- `POST /ecommerce/orders/{id}/confirm-payment` - Confirmar pago

### 4. **Tracking** (Directo desde WooCommerce)
- `GET /ecommerce/orders/{id}/tracking` - Obtener tracking
- `POST /ecommerce/orders/{id}/tracking` - Actualizar tracking

### 5. **Cupones** (Validación en WooCommerce)
- `GET /ecommerce/coupons/{code}` - Validar cupón

### 6. **Webhooks**
- `POST /ecommerce/webhooks/woocommerce` - Webhooks de WooCommerce
- `POST /ecommerce/webhooks/payment-gateway` - Webhooks de pagos

## 🧪 **Pruebas Paso a Paso**

### Paso 1: Login
```http
POST http://localhost:8000/auth/login
Content-Type: application/json

{
  "email": "tu_email@ejemplo.com",
  "password": "tu_password"
}
```

### Paso 2: Obtener Productos
```http
GET http://localhost:8000/ecommerce/products?page=1&per_page=10
Authorization: Bearer TU_TOKEN_AQUI
```

### Paso 3: Calcular Totales del Carrito
```http
POST http://localhost:8000/ecommerce/cart/calculate
Authorization: Bearer TU_TOKEN_AQUI
Content-Type: application/json

[
  {
    "product_id": 123,
    "product_name": "Producto Ejemplo",
    "price": "25.99",
    "quantity": 2
  },
  {
    "product_id": 456,
    "product_name": "Otro Producto",
    "price": "15.50",
    "quantity": 1
  }
]
```

**Respuesta:**
```json
{
  "cart_items": [...],
  "subtotal": 67.48,
  "tax_total": 5.40,
  "shipping_total": 10.0,
  "total": 82.88
}
```

### Paso 4: Crear Orden en WooCommerce
```http
POST http://localhost:8000/ecommerce/orders
Authorization: Bearer TU_TOKEN_AQUI
Content-Type: application/json

{
  "payment_method": "stripe",
  "payment_method_title": "Credit Card (Stripe)",
  "set_paid": false,
  "billing": {
    "first_name": "Juan",
    "last_name": "Pérez",
    "company": "",
    "address_1": "Calle 123",
    "address_2": "",
    "city": "Ciudad",
    "state": "Estado",
    "postcode": "12345",
    "country": "MX",
    "email": "juan@email.com",
    "phone": "5551234567"
  },
  "shipping": {
    "first_name": "Juan",
    "last_name": "Pérez",
    "company": "",
    "address_1": "Calle 123",
    "address_2": "",
    "city": "Ciudad",
    "state": "Estado",
    "postcode": "12345",
    "country": "MX"
  },
  "line_items": [
    {
      "product_id": 123,
      "quantity": 2
    },
    {
      "product_id": 456,
      "quantity": 1
    }
  ]
}
```

**Respuesta:**
```json
{
  "id": 1234,
  "status": "pending",
  "currency": "USD",
  "total": "82.88",
  "payment_method": "stripe",
  "payment_method_title": "Credit Card (Stripe)",
  "transaction_id": null,
  "date_created": "2024-01-15T10:30:00Z",
  "date_paid": null,
  "billing": {...},
  "shipping": {...},
  "line_items": [...],
  "tracking_info": null
}
```

### Paso 5: Ver Órdenes del Cliente
```http
GET http://localhost:8000/ecommerce/orders?email=juan@email.com&page=1&per_page=10
Authorization: Bearer TU_TOKEN_AQUI
```

### Paso 6: Confirmar Pago
```http
POST http://localhost:8000/ecommerce/orders/1234/confirm-payment
Authorization: Bearer TU_TOKEN_AQUI
Content-Type: application/json

{
  "transaction_id": "pi_1234567890",
  "status": "processing"
}
```

### Paso 7: Ver Tracking
```http
GET http://localhost:8000/ecommerce/orders/1234/tracking
Authorization: Bearer TU_TOKEN_AQUI
```

### Paso 8: Validar Cupón
```http
GET http://localhost:8000/ecommerce/coupons/DESCUENTO10
Authorization: Bearer TU_TOKEN_AQUI
```

## 🔄 **Flujo Completo en la App Móvil**

### 1. **Explorar Productos**
```dart
// En Flutter
final products = await ecommerceService.getProducts(
  page: 1,
  perPage: 20,
  search: "camisa",
  category: 1
);
```

### 2. **Gestionar Carrito (En memoria)**
```dart
// En Flutter - Carrito en memoria
List<CartItem> cartItems = [];

// Agregar producto
cartItems.add(CartItem(
  productId: 123,
  productName: "Producto",
  price: 25.99,
  quantity: 2
));

// Calcular totales
final totals = await ecommerceService.calculateCartTotals(cartItems);
```

### 3. **Procesar Compra**
```dart
// En Flutter
final order = await ecommerceService.createOrder(
  billingAddress: billingAddress,
  shippingAddress: shippingAddress,
  lineItems: cartItems.map((item) => {
    "product_id": item.productId,
    "quantity": item.quantity
  }).toList()
);

// Limpiar carrito local
cartItems.clear();
```

### 4. **Seguimiento de Órdenes**
```dart
// En Flutter
final orders = await ecommerceService.getCustomerOrders(
  email: userEmail
);

final tracking = await ecommerceService.getTrackingInfo(orderId);
```

## 🎯 **Ventajas del Enfoque Proxy**

### ✅ **Ventajas:**
1. **Simplicidad:** No hay sincronización de datos
2. **Consistencia:** Todo se maneja en WooCommerce
3. **Mantenimiento:** Menos código que mantener
4. **Funcionalidades:** Aprovecha todas las funciones de WooCommerce
5. **Pagos:** Usa las pasarelas ya configuradas en WooCommerce

### ⚠️ **Consideraciones:**
1. **Dependencia:** Requiere conexión a internet
2. **Performance:** Cada operación requiere llamada a WooCommerce
3. **Carrito:** Se pierde al cerrar la app (a menos que lo guardes localmente)

## 🔧 **Configuración**

### Variables de Entorno (.env):
```env
# WooCommerce Integration
WC_BASE_URL=https://tu-dominio.com/wp-json/wc/v3
WC_CONSUMER_KEY=ck_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
WC_CONSUMER_SECRET=cs_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
WOO_WEBHOOK_SECRET=tu_secreto_webhook_woocommerce
PAYMENT_WEBHOOK_SECRET=tu_secreto_webhook_pasarela_pago
```

### Plugin WordPress:
- Instalar el plugin `app-tracking-bridge` para tracking
- Configurar webhooks en WooCommerce
- Configurar pasarelas de pago

## 📱 **Implementación en Flutter**

### Servicio E-commerce:
```dart
class EcommerceService {
  // Obtener productos
  Future<List<Product>> getProducts({...}) async {...}
  
  // Calcular carrito
  Future<CartTotals> calculateCartTotals(List<CartItem> items) async {...}
  
  // Crear orden
  Future<Order> createOrder(OrderRequest request) async {...}
  
  // Obtener órdenes
  Future<List<Order>> getCustomerOrders({...}) async {...}
  
  // Tracking
  Future<TrackingInfo> getTrackingInfo(int orderId) async {...}
}
```

### Carrito Local:
```dart
class CartProvider extends ChangeNotifier {
  List<CartItem> _items = [];
  
  void addItem(Product product, int quantity) {
    // Agregar a lista local
    _items.add(CartItem(...));
    notifyListeners();
  }
  
  Future<CartTotals> calculateTotals() async {
    // Llamar al backend para calcular
    return await ecommerceService.calculateCartTotals(_items);
  }
}
```

## 🚨 **Errores Comunes**

### Error: "WooCommerce credentials not configured"
- Verificar variables de entorno en `.env`
- Asegurar que las credenciales sean correctas

### Error: "Product not found"
- Verificar que el producto existe en WooCommerce
- Comprobar que el producto esté publicado

### Error: "Order creation failed"
- Verificar que los productos están disponibles
- Comprobar que las direcciones son válidas
- Verificar que el cliente existe en WooCommerce

## 🎉 **Resumen**

Este enfoque es **perfecto para tu caso** porque:

1. **La app móvil es solo una interfaz** para WooCommerce
2. **Todo el e-commerce se maneja en WordPress** como quieres
3. **No hay duplicación de datos** ni sincronización compleja
4. **Aprovecha todas las funciones** ya implementadas en WooCommerce
5. **Mantenimiento mínimo** - solo el proxy

¿Te parece bien este enfoque? ¿Quieres que ajustemos algo específico?
