# 🛒 E-commerce Proxy - Solo Interfaz para WooCommerce

## 🎯 **Enfoque: Solo Proxy/Puente**

Esta implementación actúa como **solo una interfaz** entre tu app móvil y WooCommerce. **No hay datos locales** de carrito, órdenes, etc. Todo se maneja directamente en WordPress/WooCommerce.

## 📁 **Archivos Esenciales:**

### **Backend:**
- `features/ecommerce/woocommerce_proxy.py` - Servicio proxy para WooCommerce
- `features/ecommerce/proxy_routes.py` - Rutas API proxy
- `features/ecommerce/schemas.py` - Esquemas de datos
- `features/ecommerce/models.py` - Vacío (no hay modelos locales)

### **Configuración:**
- `.env` - Credenciales WooCommerce
- `PROXY_ECOMMERCE_GUIDE.md` - Guía completa

## 🚀 **Endpoints Disponibles:**

- `GET /ecommerce/products` - Productos desde WooCommerce
- `POST /ecommerce/cart/calculate` - Calcular totales del carrito
- `POST /ecommerce/orders` - Crear orden en WooCommerce
- `GET /ecommerce/orders` - Órdenes del cliente desde WooCommerce
- `GET /ecommerce/orders/{id}/tracking` - Tracking desde WooCommerce
- `GET /ecommerce/coupons/{code}` - Validar cupón en WooCommerce

## 🔧 **Configuración Requerida:**

```env
# WooCommerce Integration
WC_BASE_URL=https://tu-dominio.com/wp-json/wc/v3
WC_CONSUMER_KEY=ck_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
WC_CONSUMER_SECRET=cs_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

## 🎯 **Flujo Simple:**

1. **App móvil** → FastAPI → **WooCommerce**
2. **No hay datos locales** (solo carrito temporal)
3. **Todo se maneja en WordPress**
4. **App solo muestra** lo que WooCommerce responde

## ✅ **Ventajas:**

- **Simplicidad:** No hay sincronización de datos
- **Consistencia:** Todo se maneja en WooCommerce
- **Mantenimiento:** Mínimo código que mantener
- **Funcionalidades:** Aprovecha todo lo de WooCommerce
- **Pagos:** Usa las pasarelas ya configuradas

## 📱 **Para el Frontend:**

- **Carrito:** Se maneja en memoria/local
- **Órdenes:** Se obtienen de WooCommerce
- **Pagos:** Se procesan a través de WooCommerce
- **Tracking:** Se obtiene de WooCommerce

---

**Nota:** Este es el enfoque correcto para tu caso. La app móvil es solo una interfaz para WooCommerce.
