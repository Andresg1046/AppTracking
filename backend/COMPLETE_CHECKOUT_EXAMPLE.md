# 🛒 Ejemplo Completo de Checkout - Todos los Campos

## 🎯 **Endpoint Completo para Crear Orden**

```http
POST http://localhost:8000/ecommerce/orders
Authorization: Bearer TU_TOKEN_AQUI
Content-Type: application/json

{
  "payment_method": "stripe",
  "payment_method_title": "Credit Card (Stripe)",
  "set_paid": false,
  "billing": {
    "first_name": "Cristian",
    "last_name": "Gonzalez",
    "company": "",
    "address_1": "30 Central Ave, Ocean Grove",
    "address_2": "",
    "city": "Ocean Grove",
    "state": "New Jersey",
    "postcode": "07756",
    "country": "US",
    "email": "info@rubik.ec",
    "phone": "5551234567"
  },
  "shipping": {
    "first_name": "Cristian",
    "last_name": "Gonzalez",
    "company": "",
    "address_1": "30 Central Ave, Ocean Grove",
    "address_2": "",
    "city": "Ocean Grove",
    "state": "New Jersey",
    "postcode": "07756",
    "country": "US",
    "phone": "5551234567",
    "location_type": "Residence"
  },
  "line_items": [
    {
      "product_id": 123,
      "quantity": 1,
      "meta_data": [
        {
          "key": "Delivery Date",
          "value": "Tuesday, September 9, 2025"
        },
        {
          "key": "Message Card",
          "value": "Happy Birthday!"
        }
      ]
    }
  ],
  "delivery_date": "Tuesday, September 9, 2025",
  "message_card": "Happy Birthday!",
  "delivery_instructions": "Leave at front door",
  "store_pickup": false,
  "location_type": "Residence",
  "use_billing_as_shipping": true
}
```

## 🔄 **Confirmar Pago Completo**

```http
POST http://localhost:8000/ecommerce/orders/1234/confirm-payment
Authorization: Bearer TU_TOKEN_AQUI
Content-Type: application/json

{
  "transaction_id": "pi_1234567890",
  "status": "processing",
  "date_paid": "2024-01-15T10:30:00Z",
  "payment_method": "stripe",
  "payment_method_title": "Credit Card (Stripe)",
  "meta_data": [
    {
      "key": "_stripe_payment_intent_id",
      "value": "pi_1234567890"
    },
    {
      "key": "_stripe_charge_id",
      "value": "ch_1234567890"
    }
  ]
}
```

## 📱 **Flujo Completo en Flutter**

### **1. Carrito Local (Solo Visual)**
```dart
class CartItem {
  final int productId;
  final String productName;
  final double price;
  final int quantity;
  final String? deliveryDate;
  final String? messageCard;
  
  CartItem({
    required this.productId,
    required this.productName,
    required this.price,
    required this.quantity,
    this.deliveryDate,
    this.messageCard,
  });
}

// En memoria
List<CartItem> cartItems = [
  CartItem(
    productId: 123,
    productName: "Fresh And Fabulous Bouquet - Small",
    price: 54.99,
    quantity: 1,
    deliveryDate: "Tuesday, September 9, 2025",
    messageCard: "Happy Birthday!"
  )
];
```

### **2. Calcular Totales**
```dart
// Llamar al backend para calcular totales reales
final cartTotals = await ecommerceService.calculateCartTotals(cartItems);

// Mostrar en UI:
// Subtotal: $54.99
// Tax: $4.30 (calculado por WooCommerce según NJ)
// Total: $69.29
```

### **3. Recopilar Datos de Delivery**
```dart
class DeliveryInfo {
  final String firstName;
  final String lastName;
  final String address1;
  final String city;
  final String state;
  final String postcode;
  final String country;
  final String? phone;
  final String? locationType;
  final String? deliveryDate;
  final String? messageCard;
  final String? deliveryInstructions;
  final bool storePickup;
  
  DeliveryInfo({
    required this.firstName,
    required this.lastName,
    required this.address1,
    required this.city,
    required this.state,
    required this.postcode,
    required this.country,
    this.phone,
    this.locationType,
    this.deliveryDate,
    this.messageCard,
    this.deliveryInstructions,
    this.storePickup = false,
  });
}

// Datos del formulario
final deliveryInfo = DeliveryInfo(
  firstName: "Cristian",
  lastName: "Gonzalez",
  address1: "30 Central Ave, Ocean Grove",
  city: "Ocean Grove",
  state: "New Jersey",
  postcode: "07756",
  country: "US",
  phone: "5551234567",
  locationType: "Residence",
  deliveryDate: "Tuesday, September 9, 2025",
  messageCard: "Happy Birthday!",
  deliveryInstructions: "Leave at front door",
  storePickup: false,
);
```

### **4. Recopilar Datos de Billing**
```dart
class BillingInfo {
  final String firstName;
  final String lastName;
  final String email;
  final String address1;
  final String city;
  final String state;
  final String postcode;
  final String country;
  final String? phone;
  
  BillingInfo({
    required this.firstName,
    required this.lastName,
    required this.email,
    required this.address1,
    required this.city,
    required this.state,
    required this.postcode,
    required this.country,
    this.phone,
  });
}

// Datos del formulario
final billingInfo = BillingInfo(
  firstName: "Cristian",
  lastName: "Gonzalez",
  email: "info@rubik.ec",
  address1: "30 Central Ave, Ocean Grove",
  city: "Ocean Grove",
  state: "New Jersey",
  postcode: "07756",
  country: "US",
  phone: "5551234567",
);
```

### **5. Procesar Pago**
```dart
// Integración con Stripe
final paymentResult = await StripeService.processPayment(
  amount: cartTotals.total,
  currency: "USD",
  paymentMethod: "stripe",
  billingDetails: billingInfo,
);

// paymentResult.paymentIntentId = "pi_1234567890"
```

### **6. Crear Orden Final**
```dart
// Crear orden en WooCommerce
final order = await ecommerceService.createOrder(
  billingAddress: billingInfo,
  shippingAddress: deliveryInfo,
  lineItems: cartItems,
  paymentMethod: "stripe",
  paymentIntentId: paymentResult.paymentIntentId,
  deliveryDate: deliveryInfo.deliveryDate,
  messageCard: deliveryInfo.messageCard,
  deliveryInstructions: deliveryInfo.deliveryInstructions,
  storePickup: deliveryInfo.storePickup,
  locationType: deliveryInfo.locationType,
);

// Limpiar carrito local
cartItems.clear();
```

### **7. Confirmar Pago**
```dart
// Confirmar pago en WooCommerce
final confirmedOrder = await ecommerceService.confirmPayment(
  orderId: order.id,
  transactionId: paymentResult.paymentIntentId,
  status: "processing",
  paymentMethod: "stripe",
  paymentMethodTitle: "Credit Card (Stripe)",
);
```

## 🎯 **Campos Implementados**

### **✅ Delivery Fields:**
- `delivery_date` - Fecha de entrega
- `message_card` - Mensaje de la tarjeta
- `delivery_instructions` - Instrucciones de entrega
- `store_pickup` - Recogida en tienda
- `location_type` - Tipo de ubicación (Residence, Business, etc.)
- `use_billing_as_shipping` - Usar dirección de facturación

### **✅ Billing Fields:**
- `first_name`, `last_name` - Nombre completo
- `email` - Email de facturación
- `address_1`, `address_2` - Dirección
- `city`, `state`, `postcode`, `country` - Ubicación
- `phone` - Teléfono

### **✅ Shipping Fields:**
- Todos los campos de billing
- `location_type` - Tipo de ubicación adicional

### **✅ Payment Fields:**
- `transaction_id` - ID de transacción
- `date_paid` - Fecha de pago
- `payment_method` - Método de pago
- `payment_method_title` - Título del método
- `meta_data` - Datos adicionales de la pasarela

## 🚨 **Importante**

1. **Tax se calcula en WooCommerce** - No en la app móvil
2. **Todos los campos se envían a WooCommerce** tal cual
3. **La app móvil solo muestra** la respuesta de WooCommerce
4. **Meta data se guarda** en WordPress para futuras referencias

¡Listo para probar! 🎉
