"""
Servicio de Checkout Multi-Paso - Reemplaza la lógica del plugin WordPress
"""
import stripe
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from features.ecommerce.validation_service import ValidationService
from features.ecommerce.woocommerce_proxy import WooCommerceProxy
from features.ecommerce.tax_service import TaxService
from features.ecommerce.shipping_service import ShippingService
from features.ecommerce.schemas import (
    CheckoutStep1Request, CheckoutStep1Response,
    CheckoutStep2Request, CheckoutStep2Response, 
    CheckoutStep3Request, CheckoutStep3Response,
    ZipCodeValidationRequest, ZipCodeValidationResponse,
    DeliveryDateRequest, DeliveryDateResponse,
    CheckoutValidationRequest, CheckoutValidationResponse,
    OrderCreate, OrderResponse, TrackingInfo
)
import logging

logger = logging.getLogger(__name__)

class CheckoutService:
    """Servicio de checkout multi-paso"""
    
    def __init__(self):
        self.validation_service = ValidationService()
        self.woo_proxy = WooCommerceProxy()
        self.tax_service = TaxService()
        self.shipping_service = ShippingService()
        self._setup_stripe()
        # Sincronizar automáticamente con WooCommerce al inicializar
        self._sync_with_woocommerce()
    
    def _setup_stripe(self):
        """Configurar Stripe según el modo - TEMPORALMENTE DESHABILITADO"""
        # Stripe se configurará cuando esté listo para probar pagos
        logger.info("Stripe temporalmente deshabilitado - se configurará cuando esté listo para probar pagos")
        pass
    
    def _sync_with_woocommerce(self):
        """Sincronizar configuración con WooCommerce al inicializar"""
        try:
            import asyncio
            # Ejecutar sincronización de forma asíncrona
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.shipping_service.sync_with_woocommerce_shipping(self.woo_proxy))
            loop.close()
        except Exception as e:
            logger.warning(f"Could not sync with WooCommerce on startup: {str(e)}")
    
    # === PASO 1: INFORMACIÓN DE ENVÍO ===
    
    async def process_step1(self, request: CheckoutStep1Request) -> CheckoutStep1Response:
        """Procesar paso 1: Información de envío"""
        try:
            errors = []
            
            # Validar código postal si no es store pickup
            location_info = None
            if not request.use_for_storepickup:
                is_valid_zip, zip_error, location_info = await self.validation_service.validate_zip_code(
                    request.shipping_postcode
                )
                if not is_valid_zip:
                    errors.append(zip_error)
            else:
                # Para Store Pickup, no validar código postal
                location_info = {
                    "city": "Store Location",
                    "state": "NJ",
                    "state_name": "New Jersey",
                    "country": "United States"
                }
            
            # Validar campos requeridos
            fields_dict = request.dict()
            is_valid_fields, field_errors = self.validation_service.validate_checkout_fields(
                fields_dict, request.use_for_storepickup
            )
            errors.extend(field_errors)
            
            # Calcular fecha de entrega si no se proporciona
            delivery_date = request.delivery_date
            hidden_delivery_date = None
            
            if not delivery_date:
                delivery_date, hidden_delivery_date = self.validation_service.calculate_delivery_date()
            
            # Obtener fechas disponibles
            available_dates = self.validation_service.get_available_delivery_dates()
            
            return CheckoutStep1Response(
                is_valid=len(errors) == 0,
                errors=errors,
                location_info=location_info,
                delivery_date=delivery_date,
                hidden_delivery_date=hidden_delivery_date,
                available_delivery_dates=available_dates
            )
            
        except Exception as e:
            logger.error(f"Error processing step 1: {str(e)}")
            return CheckoutStep1Response(
                is_valid=False,
                errors=[f"Error interno: {str(e)}"]
            )
    
    # === PASO 2: INFORMACIÓN DE FACTURACIÓN Y PAGO ===
    
    async def process_step2(self, request: CheckoutStep2Request, step1_data: CheckoutStep1Request) -> CheckoutStep2Response:
        """Procesar paso 2: Información de facturación y pago"""
        try:
            errors = []
            
            # Validar campos de facturación
            fields_dict = request.dict()
            is_valid_fields, field_errors = self.validation_service.validate_checkout_fields(
                fields_dict, False
            )
            errors.extend(field_errors)
            
            # Validar método de pago
            is_valid_payment, payment_error = self.validation_service.validate_payment_method(
                request.payment_method
            )
            if not is_valid_payment:
                errors.append(payment_error)
            
            # Calcular impuestos si no hay errores
            tax_calculation = None
            if len(errors) == 0:
                try:
                    # Preparar dirección de envío para cálculo de impuestos
                    shipping_address = {
                        "state": step1_data.shipping_state,
                        "postcode": step1_data.shipping_postcode,
                        "city": step1_data.shipping_city,
                        "address_1": step1_data.shipping_address_1,
                        "country": step1_data.shipping_country
                    }
                    
                    # Preparar dirección de facturación
                    billing_address = {
                        "state": request.billing_state,
                        "postcode": request.billing_postcode,
                        "city": request.billing_city,
                        "address_1": request.billing_address_1,
                        "country": request.billing_country
                    }
                    
                    # Calcular envío primero
                    temp_subtotal = 50.00  # TODO: Obtener del carrito real
                    
                    if step1_data.use_for_storepickup:
                        # Para Store Pickup, usar método local_pickup
                        shipping_calculation = self.shipping_service.calculate_total_with_shipping(
                            subtotal=temp_subtotal,
                            shipping_method_id="local_pickup",
                            zip_code="00000",  # Código postal dummy para pickup
                            cart_total=temp_subtotal
                        )
                    else:
                        # Para envío normal
                        shipping_calculation = self.shipping_service.calculate_total_with_shipping(
                            subtotal=temp_subtotal,
                            shipping_method_id="flat_rate",  # TODO: Obtener método seleccionado
                            zip_code=step1_data.shipping_postcode,
                            cart_total=temp_subtotal
                        )
                    
                    # Calcular impuestos sobre subtotal + envío
                    total_before_tax = shipping_calculation.get("total_before_tax", temp_subtotal)
                    tax_calculation = self.tax_service.calculate_tax(
                        subtotal=total_before_tax,
                        shipping_address=shipping_address,
                        billing_address=billing_address,
                        customer_id=None  # TODO: Obtener customer_id real
                    )
                    
                except Exception as e:
                    logger.error(f"Error calculating tax: {str(e)}")
                    # No agregar error crítico, solo log
                    tax_calculation = {
                        "subtotal": temp_subtotal,
                        "total_tax_rate": 0.0,
                        "total_tax_amount": 0.0,
                        "reason": f"Tax calculation error: {str(e)}"
                    }
            
            # Crear PaymentIntent si es Stripe - TEMPORALMENTE DESHABILITADO
            payment_intent = None
            if request.payment_method.startswith("stripe") and len(errors) == 0:
                # Stripe se configurará cuando esté listo para probar pagos
                logger.info("PaymentIntent temporalmente deshabilitado - se configurará cuando esté listo para probar pagos")
                payment_intent = {
                    "id": "temp_payment_intent",
                    "client_secret": "temp_client_secret",
                    "status": "requires_payment_method",
                    "amount": 50.00,  # $50.00 en dólares
                    "currency": "usd"
                }
            
            return CheckoutStep2Response(
                is_valid=len(errors) == 0,
                errors=errors,
                payment_intent=payment_intent,
                tax_calculation=tax_calculation,
                shipping_calculation=shipping_calculation
            )
            
        except Exception as e:
            logger.error(f"Error processing step 2: {str(e)}")
            return CheckoutStep2Response(
                is_valid=False,
                errors=[f"Error interno: {str(e)}"]
            )
    
    # === PASO 3: REVISIÓN Y CONFIRMACIÓN ===
    
    async def process_step3(self, request: CheckoutStep3Request, step1_data: CheckoutStep1Request, step2_data: CheckoutStep2Request) -> CheckoutStep3Response:
        """Procesar paso 3: Crear orden final"""
        try:
            # Preparar datos de facturación
            billing_data = {
                "first_name": step2_data.billing_first_name,
                "last_name": step2_data.billing_last_name,
                "company": "",
                "address_1": step2_data.billing_address_1,
                "address_2": step2_data.billing_address_2 or "",
                "city": step2_data.billing_city,
                "state": step2_data.billing_state,
                "postcode": step2_data.billing_postcode,
                "country": step2_data.billing_country,
                "email": step2_data.billing_email,
                "phone": step2_data.billing_phone
            }
            
            # Preparar datos de envío
            shipping_data = None
            if not step1_data.use_for_storepickup:
                shipping_data = {
                    "first_name": step1_data.shipping_first_name,
                    "last_name": step1_data.shipping_last_name,
                    "company": "",
                    "address_1": step1_data.shipping_address_1,
                    "address_2": step1_data.shipping_address_2 or "",
                    "city": step1_data.shipping_city,
                    "state": step1_data.shipping_state,
                    "postcode": step1_data.shipping_postcode,
                    "country": step1_data.shipping_country,
                    "phone": step1_data.shipping_phone or ""
                }
            
            # Crear orden en WooCommerce
            order_create = OrderCreate(
                payment_method=step2_data.payment_method,
                payment_method_title=step2_data.payment_method_title or "Credit Card (Stripe)",
                set_paid=False,  # Se marcará como pagado cuando se confirme el pago
                billing=billing_data,
                shipping=shipping_data,
                line_items=request.cart_items,
                shipping_lines=request.shipping_lines or [],
                coupon_lines=request.coupon_lines or [],
                delivery_date=step1_data.delivery_date,
                message_card=step1_data.message_card,
                delivery_instructions=step1_data.delivery_instructions,
                store_pickup=step1_data.use_for_storepickup,
                location_type="home" if not step1_data.use_for_storepickup else "store"
            )
            
            # Crear orden en WooCommerce
            order = await self.woo_proxy.create_order(order_create)
            
            # Obtener información de tracking
            tracking_info = order.tracking_info
            
            return CheckoutStep3Response(
                order=order,
                payment_status="pending",
                tracking_info=tracking_info
            )
            
        except Exception as e:
            logger.error(f"Error processing step 3: {str(e)}")
            raise Exception(f"Error al crear orden: {str(e)}")
    
    # === VALIDACIONES INDIVIDUALES ===
    
    async def validate_zip_code(self, request: ZipCodeValidationRequest) -> ZipCodeValidationResponse:
        """Validar código postal individualmente"""
        try:
            is_valid, error_message, location_info = await self.validation_service.validate_zip_code(
                request.zip_code
            )
            
            return ZipCodeValidationResponse(
                is_valid=is_valid,
                error_message=error_message,
                location_info=location_info
            )
            
        except Exception as e:
            logger.error(f"Error validating zip code: {str(e)}")
            return ZipCodeValidationResponse(
                is_valid=False,
                error_message=f"Error interno: {str(e)}"
            )
    
    async def get_delivery_dates(self, request: DeliveryDateRequest) -> DeliveryDateResponse:
        """Obtener fechas de entrega disponibles"""
        try:
            if request.delivery_date:
                # Validar fecha específica
                is_valid, error_message = self.validation_service.validate_delivery_date(
                    request.delivery_date
                )
                if not is_valid:
                    raise ValueError(error_message)
            
            # Calcular fecha por defecto
            formatted_date, hidden_date = self.validation_service.calculate_delivery_date()
            
            # Obtener fechas disponibles
            available_dates = self.validation_service.get_available_delivery_dates()
            
            return DeliveryDateResponse(
                formatted_date=formatted_date,
                hidden_date=hidden_date,
                available_dates=available_dates
            )
            
        except Exception as e:
            logger.error(f"Error getting delivery dates: {str(e)}")
            raise Exception(f"Error al obtener fechas de entrega: {str(e)}")
    
    async def validate_checkout_step(self, request: CheckoutValidationRequest) -> CheckoutValidationResponse:
        """Validar un paso específico del checkout"""
        try:
            errors = []
            warnings = []
            next_step = None
            
            if request.step == 1:
                # Validar paso 1
                step1_data = CheckoutStep1Request(**request.data)
                step1_response = await self.process_step1(step1_data)
                errors.extend(step1_response.errors)
                
                if step1_response.is_valid:
                    next_step = 2
            
            elif request.step == 2:
                # Validar paso 2
                step2_data = CheckoutStep2Request(**request.data)
                # Necesitaríamos los datos del paso 1 para validación completa
                fields_dict = step2_data.dict()
                is_valid_fields, field_errors = self.validation_service.validate_checkout_fields(
                    fields_dict, request.is_store_pickup
                )
                errors.extend(field_errors)
                
                if len(errors) == 0:
                    next_step = 3
            
            elif request.step == 3:
                # Validar paso 3
                if not request.data.get("final_confirmation"):
                    errors.append("Se requiere confirmación final")
                else:
                    next_step = None  # Completado
            
            return CheckoutValidationResponse(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                next_step=next_step
            )
            
        except Exception as e:
            logger.error(f"Error validating checkout step: {str(e)}")
            return CheckoutValidationResponse(
                is_valid=False,
                errors=[f"Error interno: {str(e)}"]
            )
    
    # === CONFIRMACIÓN DE PAGO ===
    
    async def confirm_payment(self, order_id: int, payment_intent_id: str) -> OrderResponse:
        """Confirmar pago de una orden - TEMPORALMENTE DESHABILITADO"""
        try:
            # Stripe se configurará cuando esté listo para probar pagos
            logger.info("Confirmación de pago temporalmente deshabilitada - se configurará cuando esté listo para probar pagos")
            
            # Simular confirmación de pago
            from features.ecommerce.schemas import PaymentConfirm
            payment_data = PaymentConfirm(
                transaction_id=f"temp_txn_{order_id}",
                status="processing",
                date_paid=datetime.now(),
                payment_method="stripe",
                payment_method_title="Credit Card (Stripe) - Test Mode"
            )
            
            order = await self.woo_proxy.confirm_payment(order_id, payment_data)
            
            return order
            
        except Exception as e:
            logger.error(f"Error confirming payment for order {order_id}: {str(e)}")
            raise Exception(f"Error al confirmar pago: {str(e)}")
