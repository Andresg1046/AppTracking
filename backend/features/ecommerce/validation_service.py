"""
Servicio de validación para checkout - Reemplaza la lógica del plugin WordPress
"""
import httpx
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ValidationService:
    """Servicio centralizado de validaciones para checkout"""
    
    def __init__(self):
        # Códigos postales válidos - deberían venir de configuración
        self.valid_zip_codes = [
            "07728", "08527", "07731", "07727", "07722", "07746", "07738", 
            "08701", "07721", "07747", "08879", "08857", "07751", "07733", "07730", "08520", 
            "08831", "08828", "08501", "08535", "08555", "08510", "08759", "08757", "08755", "08733", 
            "08753", "08751", "08735", "08723", "08738", "08724", "08742", "08730", "08720", "08736", 
            "08750", "07762", "07719", "07753", "07717", "07720", "07711", "07723", "07755", 
            "07740", "07764", "07757", "07750", "07703", "07702", "07739", "07704", "07716", "07737", 
            "07718", "07756", "07701", "07712", "07724", "07726", "07734", "07740", "07748", "07758",
            "07760", "", "08514", "08535", "08816", "08872", "08884"
        ]
        
        # Configuración de entrega
        self.cutoff_time = 15  # 3:00 PM
        self.delivery_days = {
            "monday": True,
            "tuesday": True, 
            "wednesday": True,
            "thursday": True,
            "friday": True,
            "saturday": True,
            "sunday": False  # No entregas domingos
        }
    
    async def validate_zip_code(self, zip_code: str) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """
        Validar código postal y obtener información de ubicación
        
        Returns:
            (is_valid, error_message, location_info)
        """
        try:
            zip_code = zip_code.strip()
            
            # Validación básica
            if len(zip_code) != 5 or not zip_code.isdigit():
                return False, "Código postal debe tener 5 dígitos", None
            
            # Verificar si está en la lista de códigos válidos
            if zip_code not in self.valid_zip_codes:
                return False, "Oops! ZipCode not valid for delivery, choose another.", None
            
            # Obtener información de ubicación usando API externa
            location_info = await self._get_location_info(zip_code)
            
            return True, None, location_info
            
        except Exception as e:
            logger.error(f"Error validating zip code {zip_code}: {str(e)}")
            return False, "Error al validar código postal", None
    
    async def _get_location_info(self, zip_code: str) -> Optional[Dict]:
        """Obtener información de ciudad y estado desde API externa"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"https://api.zippopotam.us/us/{zip_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("places") and len(data["places"]) > 0:
                        place = data["places"][0]
                        return {
                            "city": place.get("place name"),
                            "state": place.get("state abbreviation"),
                            "state_name": place.get("state"),
                            "country": data.get("country")
                        }
        except Exception as e:
            logger.error(f"Error getting location info for {zip_code}: {str(e)}")
        
        return None
    
    def validate_checkout_fields(self, fields: Dict[str, str], is_store_pickup: bool = False) -> Tuple[bool, List[str]]:
        """
        Validar campos de checkout
        
        Args:
            fields: Diccionario con los campos del formulario
            is_store_pickup: Si es recogida en tienda
        
        Returns:
            (is_valid, error_messages)
        """
        errors = []
        
        if is_store_pickup:
            # Para Store Pickup, solo validar campos básicos
            required_fields = [
                ("billing_first_name", "Nombre"),
                ("billing_last_name", "Apellido"),
                ("billing_email", "Email"),
                ("billing_phone", "Teléfono")
            ]
            
            for field_key, field_name in required_fields:
                if not fields.get(field_key, "").strip():
                    errors.append(f"{field_name} es requerido para recogida en tienda")
        else:
            # Para envío normal, validar campos de envío
            required_shipping_fields = [
                ("shipping_first_name", "Nombre de envío"),
                ("shipping_last_name", "Apellido de envío"), 
                ("shipping_address_1", "Dirección de envío"),
                ("shipping_city", "Ciudad de envío"),
                ("shipping_state", "Estado de envío"),
                ("shipping_postcode", "Código postal de envío")
            ]
            
            for field_key, field_name in required_shipping_fields:
                if not fields.get(field_key, "").strip():
                    errors.append(f"{field_name} es requerido")
            
            # Validar código postal para envío
            zip_code = fields.get("shipping_postcode", "").strip()
            if zip_code and zip_code not in self.valid_zip_codes:
                errors.append("Código postal no válido para envío")
        
        # Siempre validar campos de facturación (excepto para Store Pickup que ya se validaron arriba)
        if not is_store_pickup:
            required_billing_fields = [
                ("billing_first_name", "Nombre de facturación"),
                ("billing_last_name", "Apellido de facturación"),
                ("billing_address_1", "Dirección de facturación"),
                ("billing_city", "Ciudad de facturación"),
                ("billing_state", "Estado de facturación"),
                ("billing_postcode", "Código postal de facturación"),
                ("billing_email", "Email"),
                ("billing_phone", "Teléfono")
            ]
            
            for field_key, field_name in required_billing_fields:
                if not fields.get(field_key, "").strip():
                    errors.append(f"{field_name} es requerido")
        
        # Validar email
        email = fields.get("billing_email", "")
        if email and "@" not in email:
            errors.append("Email no válido")
        
        return len(errors) == 0, errors
    
    def calculate_delivery_date(self, current_time: Optional[datetime] = None) -> Tuple[str, str]:
        """
        Calcular fecha de entrega basada en hora actual
        
        Returns:
            (formatted_date, hidden_date)
        """
        if current_time is None:
            current_time = datetime.now()
        
        # Verificar si ya pasó la hora límite (3:00 PM)
        cutoff_datetime = current_time.replace(hour=self.cutoff_time, minute=0, second=0, microsecond=0)
        
        if current_time > cutoff_datetime:
            # Si ya pasó la hora límite, entregar al día siguiente
            delivery_date = current_time + timedelta(days=1)
        else:
            # Entregar el mismo día
            delivery_date = current_time
        
        # Asegurar que sea un día de entrega válido
        while not self.delivery_days[delivery_date.strftime("%A").lower()]:
            delivery_date += timedelta(days=1)
        
        # Formatear fechas
        formatted_date = delivery_date.strftime("%A, %B %d, %Y")
        hidden_date = delivery_date.strftime("%d-%m-%Y")
        
        return formatted_date, hidden_date
    
    def validate_delivery_date(self, delivery_date: str, current_time: Optional[datetime] = None) -> Tuple[bool, str]:
        """
        Validar si una fecha de entrega es válida
        
        Returns:
            (is_valid, error_message)
        """
        try:
            if current_time is None:
                current_time = datetime.now()
            
            # Parsear fecha de entrega
            parsed_date = datetime.strptime(delivery_date, "%d-%m-%Y")
            
            # Verificar que no sea en el pasado
            if parsed_date.date() < current_time.date():
                return False, "La fecha de entrega no puede ser en el pasado"
            
            # Verificar que sea un día de entrega válido
            day_name = parsed_date.strftime("%A").lower()
            if not self.delivery_days[day_name]:
                return False, "No hay entregas los domingos"
            
            return True, ""
            
        except ValueError:
            return False, "Formato de fecha inválido"
        except Exception as e:
            logger.error(f"Error validating delivery date {delivery_date}: {str(e)}")
            return False, "Error al validar fecha de entrega"
    
    def get_available_delivery_dates(self, days_ahead: int = 14) -> List[Dict[str, str]]:
        """
        Obtener fechas de entrega disponibles
        
        Returns:
            Lista de fechas disponibles con formato
        """
        available_dates = []
        current_date = datetime.now().date()
        
        for i in range(days_ahead):
            check_date = current_date + timedelta(days=i)
            day_name = check_date.strftime("%A").lower()
            
            if self.delivery_days[day_name]:
                formatted_date = check_date.strftime("%A, %B %d, %Y")
                hidden_date = check_date.strftime("%d-%m-%Y")
                
                available_dates.append({
                    "formatted": formatted_date,
                    "hidden": hidden_date,
                    "date": check_date.isoformat()
                })
        
        return available_dates
    
    def copy_shipping_to_billing(self, shipping_data: Dict[str, str]) -> Dict[str, str]:
        """
        Copiar datos de envío a facturación
        
        Returns:
            Datos de facturación
        """
        billing_data = {}
        
        for key, value in shipping_data.items():
            if key.startswith("shipping_"):
                billing_key = key.replace("shipping_", "billing_")
                billing_data[billing_key] = value
        
        return billing_data
    
    def validate_payment_method(self, payment_method: str) -> Tuple[bool, str]:
        """
        Validar método de pago
        
        Returns:
            (is_valid, error_message)
        """
        valid_methods = [
            "stripe_cc",
            "stripe", 
            "stripe_applepay",
            "cod",  # Cash on delivery
            "paypal"
        ]
        
        if payment_method not in valid_methods:
            return False, f"Método de pago {payment_method} no válido"
        
        return True, ""
    
    def get_default_payment_method(self) -> str:
        """Obtener método de pago por defecto"""
        return "stripe_cc"
