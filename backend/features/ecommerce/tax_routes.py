"""
Rutas para Manejo de Impuestos - Sistema completo de impuestos
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db
from core.security import get_current_user
from features.users.models import User
from features.ecommerce.tax_service import TaxService
from features.ecommerce.schemas import (
    TaxCalculationRequest, TaxCalculationResponse,
    TaxRateRequest, TaxRateResponse,
    TaxIdValidationRequest, TaxIdValidationResponse,
    TaxExemptRequest, TaxExemptResponse
)
import logging

logger = logging.getLogger(__name__)

tax_router = APIRouter()

# Instancia del servicio de impuestos
tax_service = TaxService()

# === CÁLCULO DE IMPUESTOS ===

@tax_router.post("/calculate", response_model=TaxCalculationResponse)
async def calculate_tax(
    request: TaxCalculationRequest,
    db: Session = Depends(get_db)
):
    """
    Calcular impuestos para una orden
    
    - Calcula impuestos estatales y locales
    - Considera nexus (presencia física en el estado)
    - Maneja exenciones de impuestos
    - Proporciona desglose detallado
    """
    try:
        tax_result = tax_service.calculate_tax(
            subtotal=request.subtotal,
            shipping_address=request.shipping_address,
            billing_address=request.billing_address,
            line_items=request.line_items,
            customer_id=request.customer_id
        )
        
        return TaxCalculationResponse(**tax_result)
        
    except Exception as e:
        logger.error(f"Error calculating tax: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al calcular impuestos: {str(e)}"
        )

@tax_router.get("/rates/{state}", response_model=TaxRateResponse)
async def get_tax_rates(
    state: str,
    zip_code: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Obtener tasas de impuestos por estado y código postal
    
    - Tasas estatales
    - Tasas locales por código postal
    - Tasa total combinada
    """
    try:
        rates = tax_service.get_tax_rates_by_location(state, zip_code)
        return TaxRateResponse(**rates)
        
    except Exception as e:
        logger.error(f"Error getting tax rates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener tasas de impuestos: {str(e)}"
        )

# === VALIDACIÓN DE TAX ID ===

@tax_router.post("/validate-tax-id", response_model=TaxIdValidationResponse)
async def validate_tax_id(
    request: TaxIdValidationRequest,
    db: Session = Depends(get_db)
):
    """
    Validar Tax ID (EIN, SSN, etc.)
    
    - Valida formato de EIN (Employer Identification Number)
    - Valida formato de SSN (Social Security Number)
    - Formatea el Tax ID correctamente
    - Verifica reglas de validación específicas
    """
    try:
        result = await tax_service.validate_tax_id(request.tax_id, request.country)
        return TaxIdValidationResponse(**result)
        
    except Exception as e:
        logger.error(f"Error validating tax ID: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al validar Tax ID: {str(e)}"
        )

# === EXENCIONES DE IMPUESTOS ===

@tax_router.post("/check-exempt", response_model=TaxExemptResponse)
async def check_tax_exempt(
    request: TaxExemptRequest,
    db: Session = Depends(get_db)
):
    """
    Verificar si cliente o producto está exento de impuestos
    
    - Verifica exenciones por cliente
    - Verifica exenciones por producto
    - Retorna razón de exención
    """
    try:
        is_exempt = tax_service.is_tax_exempt(
            customer_id=request.customer_id,
            product_sku=request.product_sku
        )
        
        reason = None
        if is_exempt:
            if request.customer_id:
                reason = "Tax exempt customer"
            elif request.product_sku:
                reason = "Tax exempt product"
        
        return TaxExemptResponse(
            is_exempt=is_exempt,
            reason=reason
        )
        
    except Exception as e:
        logger.error(f"Error checking tax exempt: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al verificar exención: {str(e)}"
        )

# === CONFIGURACIÓN DE IMPUESTOS ===

@tax_router.get("/config")
async def get_tax_config(db: Session = Depends(get_db)):
    """Obtener configuración actual de impuestos"""
    try:
        return {
            "nexus_states": tax_service.tax_config["nexus_states"],
            "default_tax_class": tax_service.tax_config["default_tax_class"],
            "tax_inclusive": tax_service.tax_config["tax_inclusive"],
            "rounding_method": tax_service.tax_config["rounding_method"],
            "supported_states": list(tax_service.state_tax_rates.keys()),
            "supported_local_zips": list(tax_service.local_tax_rates.keys())
        }
    except Exception as e:
        logger.error(f"Error getting tax config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener configuración: {str(e)}"
        )

@tax_router.get("/woocommerce-config")
async def get_woocommerce_tax_config():
    """Obtener configuración de impuestos desde WooCommerce"""
    try:
        from features.ecommerce.woocommerce_proxy import WooCommerceProxy
        
        proxy = WooCommerceProxy()
        
        # Obtener configuración de WooCommerce
        wc_tax_settings = await proxy.get_tax_settings()
        
        # Obtener órdenes recientes para analizar impuestos
        orders = await proxy._make_request("GET", "/orders", params={"per_page": 5})
        
        # Analizar tax_lines de las órdenes
        tax_analysis = []
        for order in orders:
            if order.get("tax_lines"):
                tax_analysis.append({
                    "order_id": order["id"],
                    "tax_lines": order["tax_lines"],
                    "total_tax": order.get("total_tax", "0"),
                    "currency": order.get("currency", "USD")
                })
        
        return {
            "woocommerce_settings": wc_tax_settings,
            "tax_analysis": tax_analysis,
            "summary": {
                "tax_inclusive": wc_tax_settings.get("tax_inclusive", False),
                "currency": wc_tax_settings.get("currency", "USD"),
                "has_tax_lines": len(tax_analysis) > 0,
                "sample_tax_rate": tax_analysis[0]["tax_lines"][0]["rate_percent"] if tax_analysis and tax_analysis[0]["tax_lines"] else None
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting WooCommerce tax config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener configuración de WooCommerce: {str(e)}"
        )

@tax_router.put("/config")
async def update_tax_config(
    config_updates: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar configuración de impuestos (requiere autenticación)"""
    try:
        success = tax_service.update_tax_config(config_updates)
        
        if success:
            return {"message": "Tax configuration updated successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error updating tax configuration"
            )
            
    except Exception as e:
        logger.error(f"Error updating tax config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar configuración: {str(e)}"
        )

# === ENDPOINTS DE UTILIDAD ===

@tax_router.get("/nexus-states")
async def get_nexus_states(db: Session = Depends(get_db)):
    """Obtener lista de estados donde tenemos nexus"""
    try:
        return {
            "nexus_states": tax_service.tax_config["nexus_states"],
            "nexus_info": {
                state: tax_service.state_tax_rates.get(state, {})
                for state in tax_service.tax_config["nexus_states"]
            }
        }
    except Exception as e:
        logger.error(f"Error getting nexus states: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estados de nexus: {str(e)}"
        )

@tax_router.get("/supported-locations")
async def get_supported_locations(db: Session = Depends(get_db)):
    """Obtener ubicaciones soportadas para cálculo de impuestos"""
    try:
        return {
            "states": {
                code: {
                    "name": info["name"],
                    "rate": info["rate"]
                }
                for code, info in tax_service.state_tax_rates.items()
            },
            "local_zip_codes": {
                zip_code: {
                    "name": info["name"],
                    "rate": info["rate"]
                }
                for zip_code, info in tax_service.local_tax_rates.items()
            }
        }
    except Exception as e:
        logger.error(f"Error getting supported locations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener ubicaciones soportadas: {str(e)}"
        )

# === ENDPOINT DE PRUEBA ===

@tax_router.post("/test-calculation")
async def test_tax_calculation(
    subtotal: float = 100.00,
    state: str = "NJ",
    zip_code: str = "07728",
    db: Session = Depends(get_db)
):
    """
    Endpoint de prueba para cálculo de impuestos
    Útil para testing y debugging
    """
    try:
        test_address = {
            "state": state,
            "postcode": zip_code,
            "city": "Test City",
            "address_1": "123 Test St"
        }
        
        result = tax_service.calculate_tax(
            subtotal=subtotal,
            shipping_address=test_address
        )
        
        return {
            "test_data": {
                "subtotal": subtotal,
                "state": state,
                "zip_code": zip_code
            },
            "tax_result": result
        }
        
    except Exception as e:
        logger.error(f"Error in test calculation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en cálculo de prueba: {str(e)}"
        )
