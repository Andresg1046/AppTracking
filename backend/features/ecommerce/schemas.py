"""
Esquemas Pydantic para la integración con WooCommerce
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Esquemas para productos
class ProductImage(BaseModel):
    id: int
    src: str
    name: str
    alt: str

class ProductCategory(BaseModel):
    id: int
    name: str
    slug: str

class ProductTag(BaseModel):
    id: int
    name: str
    slug: str

class WooCommerceProduct(BaseModel):
    id: int
    name: str
    slug: str
    permalink: str
    date_created: datetime
    date_modified: datetime
    type: str
    status: str
    featured: bool
    catalog_visibility: str
    description: str
    short_description: str
    sku: str
    price: str
    regular_price: str
    sale_price: Optional[str] = None
    on_sale: bool
    purchasable: bool
    total_sales: int
    virtual: bool
    downloadable: bool
    downloads: List[Dict[str, Any]]
    download_limit: int
    download_expiry: int
    external_url: str
    button_text: str
    tax_status: str
    tax_class: str
    manage_stock: bool
    stock_quantity: Optional[int] = None
    stock_status: str
    backorders: str
    backorders_allowed: bool
    backordered: bool
    sold_individually: bool
    weight: str
    dimensions: Dict[str, str]
    shipping_required: bool
    shipping_taxable: bool
    shipping_class: str
    shipping_class_id: int
    reviews_allowed: bool
    average_rating: str
    rating_count: int
    related_ids: List[int]
    upsell_ids: List[int]
    cross_sell_ids: List[int]
    parent_id: int
    purchase_note: str
    categories: List[ProductCategory]
    tags: List[ProductTag]
    images: List[ProductImage]
    attributes: List[Dict[str, Any]]
    default_attributes: List[Dict[str, Any]]
    variations: List[int]
    grouped_products: List[int]
    menu_order: int
    meta_data: List[Dict[str, Any]]

class ProductVariation(BaseModel):
    """Variación de producto (size, color, etc.)"""
    id: int
    sku: str
    price: str
    regular_price: str
    sale_price: Optional[str] = None
    on_sale: bool
    stock_status: str
    stock_quantity: Optional[int] = None
    attributes: List[Dict[str, Any]]  # [{"name": "Size", "option": "M"}]
    image: Optional[ProductImage] = None
    all_images: Optional[List[ProductImage]] = None  # Todas las imágenes disponibles

class ProductResponse(BaseModel):
    """Respuesta optimizada para móvil con variaciones"""
    id: int
    name: str
    slug: str
    price: str  # Precio base del producto padre
    regular_price: str
    sale_price: Optional[str] = None
    on_sale: bool
    stock_status: str
    stock_quantity: Optional[int] = None
    images: List[ProductImage]  # Imágenes principales
    categories: List[ProductCategory]
    short_description: str
    sku: str
    type: str  # "simple" o "variable"
    variations: Optional[List[ProductVariation]] = None  # Solo para productos variables

# Esquemas para órdenes
class OrderBilling(BaseModel):
    first_name: str
    last_name: str
    company: str = ""
    address_1: str
    address_2: str = ""
    city: str
    state: str
    postcode: str
    country: str
    email: str
    phone: str = ""

class OrderShipping(BaseModel):
    first_name: str
    last_name: str
    company: str = ""
    address_1: str
    address_2: str = ""
    city: str
    state: str
    postcode: str
    country: str
    phone: str = ""
    location_type: Optional[str] = None

class OrderLineItem(BaseModel):
    id: int
    name: str
    product_id: int
    variation_id: int
    quantity: int
    tax_class: str
    subtotal: str
    subtotal_tax: str
    total: str
    total_tax: str
    taxes: List[Dict[str, Any]]
    meta_data: List[Dict[str, Any]]
    sku: str
    price: float

class OrderShippingLine(BaseModel):
    id: int
    method_title: str
    method_id: str
    total: str
    total_tax: str
    taxes: List[Dict[str, Any]]
    meta_data: List[Dict[str, Any]]

class OrderCouponLine(BaseModel):
    id: int
    code: str
    discount: str
    discount_tax: str
    meta_data: List[Dict[str, Any]]

class TrackingInfo(BaseModel):
    carrier: Optional[str] = None
    number: Optional[str] = None
    url: Optional[str] = None
    status: Optional[str] = None
    estimated_delivery: Optional[datetime] = None
    last_updated: Optional[datetime] = None

class WooCommerceOrder(BaseModel):
    id: int
    parent_id: int
    status: str
    currency: str
    date_created: datetime
    date_modified: datetime
    discount_total: str
    discount_tax: str
    shipping_total: str
    shipping_tax: str
    cart_tax: str
    total: str
    total_tax: str
    prices_include_tax: bool
    customer_id: int
    customer_ip_address: str
    customer_user_agent: str
    customer_note: str
    billing: OrderBilling
    shipping: OrderShipping
    payment_method: str
    payment_method_title: str
    transaction_id: Optional[str] = None
    date_paid: Optional[datetime] = None
    date_completed: Optional[datetime] = None
    cart_hash: str
    number: str
    meta_data: List[Dict[str, Any]]
    line_items: List[OrderLineItem]
    tax_lines: List[Dict[str, Any]]
    shipping_lines: List[OrderShippingLine]
    fee_lines: List[Dict[str, Any]]
    coupon_lines: List[OrderCouponLine]
    refunds: List[Dict[str, Any]]
    payment_url: str
    is_editable: bool
    needs_payment: bool
    needs_processing: bool
    date_created_gmt: datetime
    date_modified_gmt: datetime
    date_completed_gmt: Optional[datetime] = None
    date_paid_gmt: Optional[datetime] = None

class OrderResponse(BaseModel):
    """Respuesta optimizada para móvil"""
    id: int
    status: str
    currency: str
    total: str
    payment_method: str
    payment_method_title: str
    transaction_id: Optional[str] = None
    date_created: datetime
    date_paid: Optional[datetime] = None
    billing: OrderBilling
    shipping: OrderShipping
    line_items: List[OrderLineItem]
    tracking_info: Optional[TrackingInfo] = None

# Esquemas para crear órdenes
class OrderCreate(BaseModel):
    payment_method: str = "stripe"
    payment_method_title: str = "Credit Card (Stripe)"
    set_paid: bool = False
    billing: OrderBilling
    shipping: Optional[OrderShipping] = None
    line_items: List[Dict[str, Any]]
    shipping_lines: Optional[List[Dict[str, Any]]] = None
    coupon_lines: Optional[List[Dict[str, Any]]] = None
    meta_data: Optional[List[Dict[str, Any]]] = None
    
    # Campos adicionales de delivery
    delivery_date: Optional[str] = None
    message_card: Optional[str] = None
    delivery_instructions: Optional[str] = None
    store_pickup: Optional[bool] = False
    location_type: Optional[str] = None
    use_billing_as_shipping: Optional[bool] = False

# Esquemas para confirmar pagos
class PaymentConfirm(BaseModel):
    transaction_id: str
    status: str = "processing"
    date_paid: Optional[datetime] = None
    payment_method: Optional[str] = None
    payment_method_title: Optional[str] = None
    meta_data: Optional[List[Dict[str, Any]]] = None

# Esquemas para actualizar tracking
class TrackingUpdate(BaseModel):
    carrier: str
    number: str
    url: Optional[str] = None
    status: str = "shipped"
    estimated_delivery: Optional[datetime] = None

# Esquemas para clientes
class WooCommerceCustomer(BaseModel):
    id: int
    date_created: datetime
    date_modified: datetime
    email: str
    first_name: str
    last_name: str
    role: str
    username: str
    billing: OrderBilling
    shipping: OrderShipping
    is_paying_customer: bool
    avatar_url: str
    meta_data: List[Dict[str, Any]]

class CustomerResponse(BaseModel):
    """Respuesta optimizada para móvil"""
    id: int
    email: str
    first_name: str
    last_name: str
    username: str
    billing: OrderBilling
    shipping: OrderShipping

# Esquemas para webhooks
class WebhookPayload(BaseModel):
    id: int
    status: str
    payment_method: str
    transaction_id: Optional[str] = None
    meta_data: Optional[List[Dict[str, Any]]] = None

# Esquemas para respuestas de API
class ProductListResponse(BaseModel):
    products: List[ProductResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

class OrderListResponse(BaseModel):
    orders: List[OrderResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

# Esquemas para carrito de WooCommerce
class CartItemRequest(BaseModel):
    """Solicitud para añadir producto al carrito"""
    session_id: str
    product_id: int
    quantity: int = 1
    variation_id: Optional[int] = None

class CartUpdateRequest(BaseModel):
    """Solicitud para actualizar cantidad en carrito"""
    cart_item_key: str
    quantity: int

class CartItem(BaseModel):
    """Item del carrito - Compatible con WooCommerce Store API"""
    key: str
    id: int  # WooCommerce usa 'id' no 'product_id'
    type: str
    quantity: int
    name: str
    prices: Dict[str, Any]  # WooCommerce devuelve precios como objeto
    totals: Dict[str, Any]  # WooCommerce devuelve totales como objeto
    variation: Optional[List[Dict[str, str]]] = None
    images: Optional[List[Dict[str, Any]]] = None
    # Campos adicionales de WooCommerce
    short_description: Optional[str] = ""
    description: Optional[str] = ""
    sku: Optional[str] = ""
    permalink: Optional[str] = None
    quantity_limits: Optional[Dict[str, Any]] = None
    sold_individually: Optional[bool] = False
    backorders_allowed: Optional[bool] = False
    show_backorder_badge: Optional[bool] = False
    low_stock_remaining: Optional[int] = None
    catalog_visibility: Optional[str] = "visible"
    extensions: Optional[Dict[str, Any]] = {}

class CartResponse(BaseModel):
    """Respuesta del carrito - Compatible con WooCommerce Store API"""
    items: List[CartItem]
    coupons: List[Dict[str, Any]] = []
    fees: List[Dict[str, Any]] = []
    totals: Dict[str, Any]  # WooCommerce devuelve totales como objeto
    shipping_address: Optional[Dict[str, Any]] = None
    billing_address: Optional[Dict[str, Any]] = None
    needs_payment: Optional[bool] = True
    needs_shipping: Optional[bool] = True
    payment_requirements: Optional[List[str]] = []
    has_calculated_shipping: Optional[bool] = False
    shipping_rates: Optional[List[Dict[str, Any]]] = []
    items_count: Optional[int] = 0
    items_weight: Optional[float] = 0
    cross_sells: Optional[List[Dict[str, Any]]] = []
    errors: Optional[List[str]] = []
    payment_methods: Optional[List[str]] = []
    extensions: Optional[Dict[str, Any]] = {}

class CartTotalsResponse(BaseModel):
    """Respuesta de totales del carrito"""
    cart_items: List[Dict[str, Any]]
    subtotal: float
    tax_total: float
    shipping_total: float
    total: float

# === ESQUEMAS PARA CHECKOUT MULTI-PASO ===

class CheckoutStep1Request(BaseModel):
    """Paso 1: Información de envío"""
    shipping_first_name: str
    shipping_last_name: str
    shipping_address_1: str
    shipping_address_2: Optional[str] = ""
    shipping_city: str
    shipping_state: str
    shipping_postcode: str
    shipping_country: str = "US"
    shipping_phone: Optional[str] = ""
    use_for_storepickup: bool = False
    use_for_billing: bool = True
    delivery_date: Optional[str] = None
    message_card: Optional[str] = None
    delivery_instructions: Optional[str] = None

class CheckoutStep1Response(BaseModel):
    """Respuesta del paso 1"""
    is_valid: bool
    errors: List[str] = []
    location_info: Optional[Dict[str, str]] = None
    delivery_date: Optional[str] = None
    hidden_delivery_date: Optional[str] = None
    available_delivery_dates: Optional[List[Dict[str, str]]] = None

class CheckoutStep2Request(BaseModel):
    """Paso 2: Información de facturación y pago"""
    billing_first_name: str
    billing_last_name: str
    billing_address_1: str
    billing_address_2: Optional[str] = ""
    billing_city: str
    billing_state: str
    billing_postcode: str
    billing_country: str = "US"
    billing_email: str
    billing_phone: str
    payment_method: str = "stripe_cc"
    payment_method_title: Optional[str] = None

class CheckoutStep2Response(BaseModel):
    """Respuesta del paso 2"""
    is_valid: bool
    errors: List[str] = []
    payment_intent: Optional[Dict[str, Any]] = None
    tax_calculation: Optional[Dict[str, Any]] = None
    shipping_calculation: Optional[Dict[str, Any]] = None

class CheckoutStep3Request(BaseModel):
    """Paso 3: Revisión y confirmación"""
    cart_items: List[Dict[str, Any]]
    shipping_lines: Optional[List[Dict[str, Any]]] = None
    coupon_lines: Optional[List[Dict[str, Any]]] = None
    final_confirmation: bool = True

class CheckoutStep3Response(BaseModel):
    """Respuesta del paso 3 - Orden creada"""
    order: OrderResponse
    payment_status: str
    tracking_info: Optional[TrackingInfo] = None

# Esquemas para validación individual
class ZipCodeValidationRequest(BaseModel):
    zip_code: str

class ZipCodeValidationResponse(BaseModel):
    is_valid: bool
    error_message: Optional[str] = None
    location_info: Optional[Dict[str, str]] = None

class DeliveryDateRequest(BaseModel):
    delivery_date: Optional[str] = None

class DeliveryDateResponse(BaseModel):
    formatted_date: str
    hidden_date: str
    available_dates: List[Dict[str, str]]

class CheckoutValidationRequest(BaseModel):
    """Validación completa de checkout"""
    step: int
    data: Dict[str, Any]
    is_store_pickup: bool = False

class CheckoutValidationResponse(BaseModel):
    """Respuesta de validación"""
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    next_step: Optional[int] = None

# === ESQUEMAS PARA IMPUESTOS ===

class TaxBreakdown(BaseModel):
    """Desglose de impuestos"""
    state_tax: Optional[Dict[str, Any]] = None
    local_tax: Optional[Dict[str, Any]] = None

class TaxCalculationRequest(BaseModel):
    """Solicitud de cálculo de impuestos"""
    subtotal: float
    shipping_address: Dict[str, str]
    billing_address: Optional[Dict[str, str]] = None
    line_items: Optional[List[Dict[str, Any]]] = None
    customer_id: Optional[int] = None

class TaxCalculationResponse(BaseModel):
    """Respuesta de cálculo de impuestos"""
    subtotal: float
    total_tax_rate: float
    total_tax_amount: float
    tax_breakdown: TaxBreakdown
    tax_address: Dict[str, str]
    nexus_state: bool
    calculation_method: str
    reason: Optional[str] = None

class TaxRateRequest(BaseModel):
    """Solicitud de tasas de impuestos por ubicación"""
    state: str
    zip_code: Optional[str] = None

class TaxRateResponse(BaseModel):
    """Respuesta de tasas de impuestos"""
    state: Dict[str, Any]
    local: Dict[str, Any]
    total_rate: float

class TaxIdValidationRequest(BaseModel):
    """Solicitud de validación de Tax ID"""
    tax_id: str
    country: str = "US"

class TaxIdValidationResponse(BaseModel):
    """Respuesta de validación de Tax ID"""
    valid: bool
    type: Optional[str] = None
    formatted: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None

class TaxExemptRequest(BaseModel):
    """Solicitud de verificación de exención de impuestos"""
    customer_id: Optional[int] = None
    product_sku: Optional[str] = None

class TaxExemptResponse(BaseModel):
    """Respuesta de exención de impuestos"""
    is_exempt: bool
    reason: Optional[str] = None

# === ESQUEMAS PARA ENVÍO ===

class ShippingMethod(BaseModel):
    """Método de envío"""
    id: str
    title: str
    description: str
    cost: float
    free: bool
    delivery_days: int
    delivery_date: str
    delivery_time: str
    available: bool

class ShippingCalculationRequest(BaseModel):
    """Solicitud de cálculo de envío"""
    zip_code: str
    cart_total: float
    selected_method: Optional[str] = None
    delivery_date: Optional[str] = None

class ShippingCalculationResponse(BaseModel):
    """Respuesta de cálculo de envío"""
    available_methods: List[ShippingMethod]
    selected_method: Optional[ShippingMethod] = None
    valid_zip: bool
    error: Optional[str] = None

class ShippingTotalRequest(BaseModel):
    """Solicitud de total con envío"""
    subtotal: float
    shipping_method_id: str
    zip_code: str
    cart_total: Optional[float] = None

class ShippingTotalResponse(BaseModel):
    """Respuesta de total con envío"""
    subtotal: float
    shipping_cost: float
    shipping_method: Optional[ShippingMethod] = None
    total_before_tax: float
    shipping_taxable: bool
    error: Optional[str] = None

class ShippingConfigResponse(BaseModel):
    """Respuesta de configuración de envío"""
    shipping_methods: Dict[str, Any]
    shipping_config: Dict[str, Any]
    valid_zip_codes: List[str]