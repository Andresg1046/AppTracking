# Sincronización con WooCommerce - Documentación

## 🔄 Visión General

El sistema ahora puede sincronizar automáticamente la configuración de envío e impuestos con WooCommerce, obteniendo los valores reales configurados en WordPress en lugar de usar valores hardcodeados.

## 🎯 Características de Sincronización

### ✅ **Sincronización Automática**
- Se ejecuta al inicializar el `CheckoutService`
- Obtiene métodos de envío reales de WooCommerce
- Actualiza costos y configuraciones dinámicamente

### ✅ **Sincronización Manual**
- Endpoints para sincronizar bajo demanda
- Verificación de configuración actual
- Debugging y troubleshooting

### ✅ **Fallback Inteligente**
- Si WooCommerce no está disponible, usa valores por defecto
- Logging detallado para debugging
- No interrumpe el funcionamiento del sistema

## 🏗️ Implementación

### **WooCommerceProxy** (`woocommerce_proxy.py`)

#### **Nuevos Métodos Agregados:**

```python
# Obtener zonas de envío
async def get_shipping_zones() -> List[Dict[str, Any]]

# Obtener métodos de una zona
async def get_shipping_zone_methods(zone_id: int) -> List[Dict[str, Any]]

# Obtener configuración de método específico
async def get_shipping_method(zone_id: int, method_id: int) -> Dict[str, Any]]

# Obtener todos los métodos de envío
async def get_all_shipping_methods() -> Dict[str, Any]

# Obtener configuración de impuestos
async def get_tax_settings() -> Dict[str, Any]
```

### **ShippingService** (`shipping_service.py`)

#### **Métodos de Sincronización:**

```python
# Sincronizar con WooCommerce
async def sync_with_woocommerce_shipping(woo_proxy) -> bool

# Actualizar métodos con datos de WC
def _update_shipping_methods_from_wc(wc_config: Dict[str, Any]) -> None

# Obtener configuración de WC
async def get_wc_shipping_config(woo_proxy) -> Dict[str, Any]
```

## 🔧 Endpoints de Sincronización

### **1. Sincronizar con WooCommerce**
```http
POST /shipping/sync-wc
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "message": "Shipping configuration synced with WooCommerce successfully",
  "synced": true
}
```

### **2. Obtener Configuración de WooCommerce**
```http
GET /shipping/wc-config
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "woocommerce_config": {
    "zones": [...],
    "methods": {...},
    "settings": {...}
  },
  "current_local_config": {
    "shipping_methods": {...},
    "shipping_config": {...}
  }
}
```

### **3. Ver Métodos de WooCommerce (Público)**
```http
GET /shipping/wc-methods
```

**Response:**
```json
{
  "woocommerce_methods": [
    {
      "zone_name": "United States (US)",
      "zone_id": 0,
      "method_id": "flat_rate",
      "title": "Delivery Service",
      "cost": "10",
      "enabled": true,
      "tax_status": "taxable",
      "settings": {...}
    }
  ],
  "total_methods": 1,
  "zones": [...]
}
```

## 📊 Flujo de Sincronización

### **1. Inicialización Automática**
```
CheckoutService.__init__() 
    ↓
_sync_with_woocommerce()
    ↓
shipping_service.sync_with_woocommerce_shipping()
    ↓
woo_proxy.get_all_shipping_methods()
    ↓
_update_shipping_methods_from_wc()
```

### **2. Sincronización Manual**
```
POST /shipping/sync-wc
    ↓
shipping_service.sync_with_woocommerce_shipping()
    ↓
Actualización en tiempo real
```

## 🔍 Datos Sincronizados

### **Método "flat_rate" (Delivery Service)**
- **Costo**: Obtenido de WooCommerce (ej: $10.00)
- **Título**: "Delivery Service" o personalizado
- **Estado**: Habilitado/Deshabilitado
- **Tax Status**: "taxable" o "none"

### **Método "local_pickup" (Store Pickup)**
- **Título**: "Store Pickup" o personalizado
- **Estado**: Habilitado/Deshabilitado
- **Tax Status**: Configurado en WooCommerce

### **Configuración General**
- **Tax Shipping**: Si los envíos están sujetos a impuestos
- **Zonas de Envío**: Ubicaciones donde están disponibles los métodos

## 🧪 Testing y Verificación

### **1. Verificar Sincronización**
```bash
# Ver métodos actuales
curl -X GET "http://localhost:8000/shipping/methods"

# Ver métodos de WooCommerce
curl -X GET "http://localhost:8000/shipping/wc-methods"

# Sincronizar manualmente
curl -X POST "http://localhost:8000/shipping/sync-wc" \
  -H "Authorization: Bearer <token>"
```

### **2. Comparar Configuraciones**
```bash
# Ver configuración completa
curl -X GET "http://localhost:8000/shipping/wc-config" \
  -H "Authorization: Bearer <token>"
```

### **3. Probar Cálculo con Datos Reales**
```bash
# Calcular envío con datos sincronizados
curl -X POST "http://localhost:8000/shipping/test-calculation?zip_code=07728&cart_total=54.99&method_id=flat_rate"
```

## 📝 Ejemplo de Sincronización

### **Antes de Sincronizar:**
```json
{
  "flat_rate": {
    "title": "Delivery Service",
    "cost": 10.00,
    "enabled": true
  }
}
```

### **Después de Sincronizar:**
```json
{
  "flat_rate": {
    "title": "Delivery Service",
    "cost": 12.50,  // ← Actualizado desde WooCommerce
    "enabled": true,
    "tax_status": "taxable"  // ← Agregado desde WooCommerce
  }
}
```

## 🚨 Manejo de Errores

### **Caso 1: WooCommerce No Disponible**
```json
{
  "message": "No shipping methods found in WooCommerce, using defaults",
  "synced": false
}
```

### **Caso 2: Error de Conexión**
```json
{
  "detail": "Error al sincronizar con WooCommerce: Connection timeout"
}
```

### **Caso 3: Datos Inválidos**
- Se mantienen valores por defecto
- Se registra error en logs
- Sistema continúa funcionando

## 🔧 Configuración

### **Variables de Entorno**
```bash
# WooCommerce API
WC_BASE_URL=https://your-domain.com/wp-json/wc/v3
WC_CONSUMER_KEY=ck_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
WC_CONSUMER_SECRET=cs_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Configuración de sincronización
WC_SYNC_ON_STARTUP=true
WC_SYNC_INTERVAL=3600  # 1 hora en segundos
```

### **Logging**
```python
# Logs de sincronización
logger.info("Shipping configuration synced with WooCommerce")
logger.warning("No shipping methods found in WooCommerce, using defaults")
logger.error("Error syncing with WooCommerce: Connection timeout")
```

## 🎯 Beneficios

### **1. Datos Reales**
- ✅ Costos actualizados desde WooCommerce
- ✅ Configuraciones sincronizadas
- ✅ Estados habilitado/deshabilitado

### **2. Mantenimiento Simplificado**
- ✅ Un solo lugar para configurar (WooCommerce)
- ✅ Cambios automáticos en la app móvil
- ✅ No necesidad de actualizar código

### **3. Consistencia**
- ✅ Mismos valores en WordPress y app móvil
- ✅ Sincronización automática
- ✅ Fallback inteligente

## 🔮 Próximas Mejoras

### **1. Sincronización Periódica**
- Cron job para sincronizar cada hora
- Webhooks de WooCommerce para cambios en tiempo real
- Cache inteligente con TTL

### **2. Sincronización Bidireccional**
- Actualizar WooCommerce desde la app
- Sincronización de órdenes
- Métricas y analytics

### **3. Configuración Avanzada**
- Múltiples zonas de envío
- Métodos por región
- Costos dinámicos por peso/volumen

---

**¡La sincronización con WooCommerce está completamente implementada!** 🎉

Ahora el sistema obtiene automáticamente los valores reales configurados en WordPress, incluyendo el costo de $10.00 del "Delivery Service" que viste en la imagen.
