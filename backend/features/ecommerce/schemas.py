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

# Esquemas para carrito (solo cálculo)
class CartTotalsResponse(BaseModel):
    cart_items: List[Dict[str, Any]]
    subtotal: float
    tax_total: float
    shipping_total: float
    total: float
