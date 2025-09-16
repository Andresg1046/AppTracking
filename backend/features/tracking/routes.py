"""
Rutas para el sistema de tracking
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from typing import List, Optional
from datetime import datetime
import asyncio
import json

from core.database import get_db
from core.security import get_current_user
from features.users.models import User
from features.tracking.models import Driver, DeliveryTracking, LocationUpdate
from features.ecommerce.models import Order
from features.tracking.services import DriverService, LocationService, DeliveryTrackingService
from features.tracking.schemas import (
    DriverActivateRequest, DriverResponse, DriverUpdateRequest,
    LocationUpdateRequest, LocationUpdateResponse, DriverStatusUpdateRequest,
    DriverStatusResponse, DriverListResponse, DeliveryTrackingCreate,
    DeliveryTrackingResponse, DeliveryStatusUpdate, TrackingOrderResponse,
    AdminDashboardResponse, DriverStatsResponse, DriverLocationResponse
)

tracking_router = APIRouter()

# === FUNCIONALIDAD 1: GESTIÓN DE CONDUCTORES ===

@tracking_router.post("/drivers/activate/{user_id}", response_model=DriverResponse)
async def activate_driver(
    user_id: int,
    driver_data: DriverActivateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Activar usuario como conductor
    - Verificar que el usuario tiene rol 'driver'
    - Crear perfil de conductor
    - Asignar vehículo si se proporciona
    """
    try:
        # Solo admins pueden activar conductores
        if not current_user.role or current_user.role.name != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo administradores pueden activar conductores"
            )
        
        driver = DriverService.activate_driver(user_id, driver_data, db)
        
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo activar el conductor"
            )
        
        # Obtener información completa del conductor
        return await _build_driver_response(driver, db)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

@tracking_router.get("/drivers/me", response_model=DriverResponse)
async def get_driver_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener perfil de conductor del usuario actual
    - Verificar que es conductor
    - Retornar información completa del conductor
    """
    try:
        # Verificar que el usuario es conductor
        if not current_user.role or current_user.role.name != "driver":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El usuario debe tener rol 'driver'"
            )
        
        driver = DriverService.get_driver_by_user_id(current_user.id, db)
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Perfil de conductor no encontrado. Debe activarse primero."
            )
        
        return await _build_driver_response(driver, db)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

@tracking_router.put("/drivers/me", response_model=DriverResponse)
async def update_driver_profile(
    update_data: DriverUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar perfil de conductor
    - Solo el conductor puede actualizar su perfil
    - Validar datos proporcionados
    """
    try:
        # Verificar que el usuario es conductor
        if not current_user.role or current_user.role.name != "driver":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El usuario debe tener rol 'driver'"
            )
        
        driver = DriverService.get_driver_by_user_id(current_user.id, db)
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Perfil de conductor no encontrado"
            )
        
        updated_driver = DriverService.update_driver_profile(driver.id, update_data, db)
        if not updated_driver:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo actualizar el perfil"
            )
        
        return await _build_driver_response(updated_driver, db)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

@tracking_router.post("/drivers/status", response_model=DriverStatusResponse)
async def update_driver_status(
    status_data: DriverStatusUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar estado del conductor (online/offline, disponible)
    - Solo el conductor puede cambiar su estado
    - Validar transiciones de estado
    """
    try:
        # Verificar que el usuario es conductor
        if not current_user.role or current_user.role.name != "driver":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El usuario debe tener rol 'driver'"
            )
        
        driver = DriverService.get_driver_by_user_id(current_user.id, db)
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Perfil de conductor no encontrado"
            )
        
        updated_driver = DriverService.update_driver_status(
            driver.id, 
            status_data.is_online, 
            status_data.is_available, 
            db
        )
        
        if not updated_driver:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo actualizar el estado"
            )
        
        return DriverStatusResponse(
            driver_id=updated_driver.id,
            is_online=updated_driver.is_online,
            is_available=updated_driver.is_available,
            is_delivering=updated_driver.is_delivering,
            current_location=updated_driver.current_location,
            last_update=updated_driver.updated_at,
            status_message="Estado actualizado correctamente"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

@tracking_router.get("/drivers/stats", response_model=DriverStatsResponse)
async def get_driver_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener estadísticas del conductor
    - Entregas completadas, tasa de éxito, etc.
    """
    try:
        # Verificar que el usuario es conductor
        if not current_user.role or current_user.role.name != "driver":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El usuario debe tener rol 'driver'"
            )
        
        driver = DriverService.get_driver_by_user_id(current_user.id, db)
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Perfil de conductor no encontrado"
            )
        
        stats = DriverService.get_driver_stats(driver.id, db)
        
        return DriverStatsResponse(
            driver_id=driver.id,
            total_deliveries=stats.get("total_deliveries", 0),
            completed_deliveries=stats.get("completed_deliveries", 0),
            failed_deliveries=stats.get("failed_deliveries", 0),
            success_rate=stats.get("success_rate", 0.0),
            average_delivery_time=None,  # TODO: Implementar cálculo
            total_distance=None,  # TODO: Implementar cálculo
            rating=None,  # TODO: Implementar sistema de calificaciones
            last_30_days={"deliveries": stats.get("recent_deliveries_30_days", 0)}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

# === FUNCIONALIDAD 2: ACTUALIZACIÓN DE UBICACIÓN ===

@tracking_router.post("/drivers/location", response_model=LocationUpdateResponse)
async def update_driver_location(
    location_data: LocationUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar ubicación del conductor
    - Validar coordenadas
    - Almacenar en historial
    - Calcular distancia a destino si hay entrega activa
    """
    try:
        # Verificar que el usuario es conductor
        if not current_user.role or current_user.role.name != "driver":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El usuario debe tener rol 'driver'"
            )
        
        driver = DriverService.get_driver_by_user_id(current_user.id, db)
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Perfil de conductor no encontrado"
            )
        
        # Actualizar ubicación
        result = LocationService.update_driver_location(driver.id, location_data, db=db)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        return LocationUpdateResponse(
            success=True,
            message=result["message"],
            timestamp=result["timestamp"],
            location=result["location"],
            distance_from_destination=result.get("distance_from_destination"),
            estimated_arrival=result.get("estimated_arrival")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

@tracking_router.get("/drivers/location/history")
async def get_location_history(
    hours: int = Query(24, ge=1, le=168, description="Horas de historial a obtener"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener historial de ubicaciones del conductor
    - Últimas N horas de ubicaciones
    - Para análisis de rutas
    """
    try:
        # Verificar que el usuario es conductor
        if not current_user.role or current_user.role.name != "driver":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El usuario debe tener rol 'driver'"
            )
        
        driver = DriverService.get_driver_by_user_id(current_user.id, db)
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Perfil de conductor no encontrado"
            )
        
        history = LocationService.get_driver_location_history(driver.id, hours, db)
        
        return {
            "driver_id": driver.id,
            "hours_requested": hours,
            "total_points": len(history),
            "location_history": history
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

@tracking_router.get("/drivers/current-location", response_model=DriverLocationResponse)
async def get_current_location(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener ubicación actual del conductor
    - Solo el conductor puede ver su ubicación
    - Retorna ubicación más reciente
    """
    try:
        # Verificar que el usuario es conductor
        if not current_user.role or current_user.role.name != "driver":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El usuario debe tener rol 'driver'"
            )
        
        driver = DriverService.get_driver_by_user_id(current_user.id, db)
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Perfil de conductor no encontrado"
            )
        
        return DriverLocationResponse(
            driver_id=driver.id,
            driver_name=driver.user.full_name if driver.user else "Conductor",
            driver_phone=driver.phone,
            is_online=driver.is_online,
            is_delivering=driver.is_delivering,
            current_location=driver.current_location,
            last_update=driver.last_location_update or driver.updated_at,
            vehicle_info={
                "brand": driver.vehicle.brand if driver.vehicle else None,
                "model": driver.vehicle.model if driver.vehicle else None,
                "plate": driver.vehicle.plate if driver.vehicle else None
            } if driver.vehicle else None,
            estimated_arrival=None,  # Se calculará cuando haya entrega
            status_message="Ubicación actual"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

@tracking_router.get("/order/{order_number}/driver-location")
async def get_driver_location_for_customer(
    order_number: str,
    db: Session = Depends(get_db)
):
    """
    Obtener ubicación del conductor para cliente
    - NO requiere autenticación
    - Para mostrar en OpenStreetMap
    """
    try:
        # Buscar orden por número
        try:
            order_id = int(order_number)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Número de orden inválido"
            )
        
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Orden no encontrada"
            )
        
        # Buscar tracking de entrega
        delivery = db.query(DeliveryTracking).filter(
            DeliveryTracking.order_id == order_id
        ).first()
        
        if not delivery or not delivery.driver:
            return {
                "order_number": order_number,
                "driver": None,
                "delivery_address": order.shipping_address or {},
                "tracking_enabled": False,
                "message": "No hay conductor asignado"
            }
        
        driver = delivery.driver
        
        return {
            "order_number": order_number,
            "driver": {
                "driver_id": driver.id,
                "driver_name": driver.user.full_name if driver.user else "Conductor",
                "driver_phone": driver.phone,
                "is_online": driver.is_online,
                "is_delivering": driver.is_delivering,
                "current_location": driver.current_location,
                "last_update": driver.last_location_update,
                "vehicle_info": {
                    "brand": driver.vehicle.brand if driver.vehicle else None,
                    "model": driver.vehicle.model if driver.vehicle else None,
                    "plate": driver.vehicle.plate if driver.vehicle else None
                } if driver.vehicle else None,
                "estimated_arrival": delivery.estimated_arrival,
                "status": delivery.status
            },
            "delivery_address": delivery.delivery_address or order.shipping_address or {},
            "tracking_enabled": True,
            "last_update": driver.last_location_update or delivery.updated_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

@tracking_router.get("/admin/drivers/locations")
async def get_all_drivers_locations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener ubicaciones de todos los conductores (solo admins)
    - Para mostrar en mapa de administración
    - Solo conductores online
    """
    try:
        # Solo admins pueden ver ubicaciones de todos los conductores
        if not current_user.role or current_user.role.name != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo administradores pueden ver ubicaciones de conductores"
            )
        
        # Obtener solo conductores online
        drivers = db.query(Driver).filter(
            Driver.is_online == True
        ).all()
        
        drivers_locations = []
        for driver in drivers:
            if driver.current_location:  # Solo si tiene ubicación
                drivers_locations.append({
                    "driver_id": driver.id,
                    "driver_name": driver.user.full_name if driver.user else "Conductor",
                    "current_location": driver.current_location,
                    "is_delivering": driver.is_delivering,
                    "last_update": driver.last_location_update,
                    "vehicle_info": {
                        "brand": driver.vehicle.brand if driver.vehicle else None,
                        "model": driver.vehicle.model if driver.vehicle else None,
                        "plate": driver.vehicle.plate if driver.vehicle else None
                    } if driver.vehicle else None
                })
        
        return {
            "drivers": drivers_locations,
            "total_online": len(drivers),
            "total_with_location": len(drivers_locations),
            "last_update": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

# === FUNCIONALIDAD 3: GESTIÓN DE ENTREGAS ===

@tracking_router.post("/deliveries/assign", response_model=DeliveryTrackingResponse)
async def assign_delivery(
    delivery_data: DeliveryTrackingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Asignar entrega a conductor
    - Solo admins pueden asignar entregas
    - Verificar disponibilidad del conductor
    - Crear tracking de entrega
    """
    try:
        # Solo admins pueden asignar entregas
        if not current_user.role or current_user.role.name != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo administradores pueden asignar entregas"
            )
        
        delivery = DeliveryTrackingService.assign_delivery(delivery_data, db)
        
        if not delivery:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo asignar la entrega"
            )
        
        return await _build_delivery_response(delivery, db)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

@tracking_router.get("/drivers/deliveries", response_model=List[DeliveryTrackingResponse])
async def get_driver_deliveries(
    status_filter: Optional[str] = Query(None, description="Filtrar por estado"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener entregas del conductor
    - Entregas asignadas, en progreso, completadas
    - Filtrar por estado si se especifica
    """
    try:
        # Verificar que el usuario es conductor
        if not current_user.role or current_user.role.name != "driver":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El usuario debe tener rol 'driver'"
            )
        
        driver = DriverService.get_driver_by_user_id(current_user.id, db)
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Perfil de conductor no encontrado"
            )
        
        deliveries = DeliveryTrackingService.get_driver_deliveries(driver.id, db, status_filter)
        
        return [await _build_delivery_response(delivery, db) for delivery in deliveries]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

@tracking_router.put("/deliveries/{delivery_id}/status", response_model=DeliveryTrackingResponse)
async def update_delivery_status(
    delivery_id: int,
    status_update: DeliveryStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar estado de entrega
    - Solo el conductor asignado puede cambiar el estado
    - Validar transiciones de estado
    """
    try:
        # Verificar que el usuario es conductor
        if not current_user.role or current_user.role.name != "driver":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El usuario debe tener rol 'driver'"
            )
        
        driver = DriverService.get_driver_by_user_id(current_user.id, db)
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Perfil de conductor no encontrado"
            )
        
        # Verificar que la entrega pertenece al conductor
        delivery = db.query(DeliveryTracking).filter(
            and_(
                DeliveryTracking.id == delivery_id,
                DeliveryTracking.driver_id == driver.id
            )
        ).first()
        
        if not delivery:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Entrega no encontrada o no asignada a este conductor"
            )
        
        updated_delivery = DeliveryTrackingService.update_delivery_status(
            delivery_id, status_update, db
        )
        
        if not updated_delivery:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo actualizar el estado de la entrega"
            )
        
        return await _build_delivery_response(updated_delivery, db)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

# === FUNCIONALIDAD 4: TRACKING PARA CLIENTES ===

@tracking_router.get("/tracking/{order_number}", response_model=TrackingOrderResponse)
async def track_order(
    order_number: str,
    db: Session = Depends(get_db)
):
    """
    Tracking de orden para cliente
    - Buscar orden por número
    - Obtener información del conductor y ubicación
    - NO requiere autenticación
    """
    try:
        # Buscar orden por número (asumiendo que order_number es el ID)
        try:
            order_id = int(order_number)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Número de orden inválido"
            )
        
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Orden no encontrada"
            )
        
        # Buscar tracking de entrega
        delivery = db.query(DeliveryTracking).filter(
            DeliveryTracking.order_id == order_id
        ).first()
        
        if not delivery:
            return TrackingOrderResponse(
                order_id=order.id,
                order_number=str(order.id),
                status="pending",
                driver=None,
                delivery_address=order.shipping_address or {},
                estimated_arrival=None,
                tracking_enabled=False,
                last_update=order.updated_at
            )
        
        # Obtener información del conductor
        driver_info = None
        if delivery.driver:
            driver_info = {
                "driver_id": delivery.driver.id,
                "driver_name": delivery.driver.user.full_name if delivery.driver.user else "Conductor",
                "driver_phone": delivery.driver.phone,
                "is_online": delivery.driver.is_online,
                "is_delivering": delivery.driver.is_delivering,
                "current_location": delivery.driver.current_location,
                "last_update": delivery.driver.last_location_update,
                "vehicle_info": {
                    "brand": delivery.driver.vehicle.brand if delivery.driver.vehicle else None,
                    "model": delivery.driver.vehicle.model if delivery.driver.vehicle else None,
                    "plate": delivery.driver.vehicle.plate if delivery.driver.vehicle else None
                } if delivery.driver.vehicle else None,
                "estimated_arrival": delivery.estimated_arrival,
                "status_message": f"Estado: {delivery.status}"
            }
        
        return TrackingOrderResponse(
            order_id=order.id,
            order_number=str(order.id),
            status=delivery.status,
            driver=driver_info,
            delivery_address=delivery.delivery_address or order.shipping_address or {},
            estimated_arrival=delivery.estimated_arrival,
            tracking_enabled=True,
            last_update=delivery.last_location_update or delivery.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

# === FUNCIONALIDAD 6: PANEL DE ADMINISTRACIÓN ===

@tracking_router.get("/admin/drivers", response_model=DriverListResponse)
async def get_all_drivers(
    online_only: bool = Query(False, description="Solo conductores online"),
    available_only: bool = Query(False, description="Solo conductores disponibles"),
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=500, description="Número máximo de registros"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener todos los conductores (solo admins)
    - Lista completa de conductores
    - Filtros por estado
    - Estadísticas agregadas
    """
    try:
        # Solo admins pueden ver todos los conductores
        if not current_user.role or current_user.role.name != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo administradores pueden ver todos los conductores"
            )
        
        drivers, total = DriverService.get_all_drivers(db, skip, limit, online_only, available_only)
        
        # Construir respuestas
        driver_responses = []
        online_count = 0
        available_count = 0
        delivering_count = 0
        
        for driver in drivers:
            response = await _build_driver_response(driver, db)
            driver_responses.append(response)
            
            if driver.is_online:
                online_count += 1
            if driver.is_available:
                available_count += 1
            if driver.is_delivering:
                delivering_count += 1
        
        return DriverListResponse(
            drivers=driver_responses,
            total=total,
            online_count=online_count,
            available_count=available_count,
            delivering_count=delivering_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

@tracking_router.get("/admin/dashboard", response_model=AdminDashboardResponse)
async def get_admin_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Dashboard de administración
    - Estadísticas generales
    - Conductores y entregas activas
    """
    try:
        # Solo admins pueden ver el dashboard
        if not current_user.role or current_user.role.name != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo administradores pueden ver el dashboard"
            )
        
        # Estadísticas generales
        total_drivers = db.query(Driver).count()
        online_drivers = db.query(Driver).filter(Driver.is_online == True).count()
        available_drivers = db.query(Driver).filter(Driver.is_available == True).count()
        delivering_drivers = db.query(Driver).filter(Driver.is_delivering == True).count()
        
        total_deliveries = db.query(DeliveryTracking).count()
        active_deliveries = db.query(DeliveryTracking).filter(
            DeliveryTracking.status.in_(["assigned", "started", "in_progress"])
        ).count()
        
        # Entregas completadas hoy
        today = datetime.utcnow().date()
        completed_deliveries_today = db.query(DeliveryTracking).filter(
            and_(
                DeliveryTracking.status == "completed",
                func.date(DeliveryTracking.completed_at) == today
            )
        ).count()
        
        # Conductores recientes (últimos 10)
        recent_drivers = db.query(Driver).order_by(desc(Driver.created_at)).limit(10).all()
        driver_responses = [await _build_driver_response(driver, db) for driver in recent_drivers]
        
        # Entregas recientes (últimas 10)
        recent_deliveries = db.query(DeliveryTracking).order_by(desc(DeliveryTracking.assigned_at)).limit(10).all()
        delivery_responses = [await _build_delivery_response(delivery, db) for delivery in recent_deliveries]
        
        return AdminDashboardResponse(
            total_drivers=total_drivers,
            online_drivers=online_drivers,
            available_drivers=available_drivers,
            delivering_drivers=delivering_drivers,
            total_deliveries=total_deliveries,
            active_deliveries=active_deliveries,
            completed_deliveries_today=completed_deliveries_today,
            drivers=driver_responses,
            recent_deliveries=delivery_responses
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

# === FUNCIONES AUXILIARES ===

async def _build_driver_response(driver: Driver, db: Session) -> DriverResponse:
    """Construir respuesta completa del conductor"""
    # Obtener información del usuario
    user_info = {
        "user_name": driver.user.full_name if driver.user else None,
        "user_email": driver.user.email if driver.user else None,
        "user_phone": driver.user.phone if driver.user else None
    }
    
    # Obtener información del vehículo
    vehicle_info = None
    if driver.vehicle:
        vehicle_info = {
            "id": driver.vehicle.id,
            "brand": driver.vehicle.brand,
            "model": driver.vehicle.model,
            "year": driver.vehicle.year,
            "color": driver.vehicle.color,
            "plate": driver.vehicle.plate,
            "state": driver.vehicle.state
        }
    
    # Obtener estadísticas
    stats = DriverService.get_driver_stats(driver.id, db)
    
    return DriverResponse(
        id=driver.id,
        user_id=driver.user_id,
        vehicle_id=driver.vehicle_id,
        is_online=driver.is_online,
        is_available=driver.is_available,
        is_delivering=driver.is_delivering,
        current_location=driver.current_location,
        last_location_update=driver.last_location_update,
        driver_license=driver.driver_license,
        phone=driver.phone,
        notes=driver.notes,
        location_update_interval=driver.location_update_interval,
        auto_location_sharing=driver.auto_location_sharing,
        created_at=driver.created_at,
        updated_at=driver.updated_at,
        **user_info,
        vehicle_info=vehicle_info,
        total_deliveries=stats.get("total_deliveries", 0),
        completed_deliveries=stats.get("completed_deliveries", 0),
        success_rate=stats.get("success_rate", 0.0)
    )

async def _build_delivery_response(delivery: DeliveryTracking, db: Session) -> DeliveryTrackingResponse:
    """Construir respuesta completa de entrega"""
    # Obtener información del conductor
    driver_info = None
    if delivery.driver:
        driver_info = {
            "id": delivery.driver.id,
            "name": delivery.driver.user.full_name if delivery.driver.user else "Conductor",
            "phone": delivery.driver.phone,
            "is_online": delivery.driver.is_online,
            "vehicle": {
                "brand": delivery.driver.vehicle.brand if delivery.driver.vehicle else None,
                "model": delivery.driver.vehicle.model if delivery.driver.vehicle else None,
                "plate": delivery.driver.vehicle.plate if delivery.driver.vehicle else None
            } if delivery.driver.vehicle else None
        }
    
    # Obtener información de la orden
    order_info = None
    if delivery.order:
        order_info = {
            "id": delivery.order.id,
            "customer_name": delivery.order.customer_name,
            "customer_email": delivery.order.customer_email,
            "total": delivery.order.total,
            "status": delivery.order.status,
            "created_at": delivery.order.created_at
        }
    
    return DeliveryTrackingResponse(
        id=delivery.id,
        order_id=delivery.order_id,
        driver_id=delivery.driver_id,
        status=delivery.status,
        priority=delivery.priority,
        assigned_at=delivery.assigned_at,
        started_at=delivery.started_at,
        completed_at=delivery.completed_at,
        delivery_address=delivery.delivery_address,
        delivery_coordinates=delivery.delivery_coordinates,
        estimated_arrival=delivery.estimated_arrival,
        estimated_duration=delivery.estimated_duration,
        delivery_notes=delivery.delivery_notes,
        customer_phone=delivery.customer_phone,
        customer_name=delivery.customer_name,
        distance_remaining=delivery.distance_remaining,
        last_location_update=delivery.last_location_update,
        driver_info=driver_info,
        order_info=order_info
    )

# ===== WEBSOCKET PARA TRACKING EN TIEMPO REAL =====

# Diccionario para almacenar conexiones WebSocket activas
active_connections: dict = {}

@tracking_router.websocket("/ws/tracking/{order_number}")
async def websocket_tracking(websocket: WebSocket, order_number: str):
    """
    WebSocket para tracking en tiempo real de órdenes
    - Cliente se conecta con número de orden
    - Recibe ubicación del conductor cada 5 segundos
    - Desconexión automática cuando conductor llega
    """
    await websocket.accept()
    
    # Agregar conexión a la lista activa
    if order_number not in active_connections:
        active_connections[order_number] = []
    active_connections[order_number].append(websocket)
    
    try:
        while True:
            # Buscar información de la orden y conductor
            db = next(get_db())
            try:
                # Buscar orden por número
                order = db.query(Order).filter(
                    Order.woocommerce_order_id == order_number
                ).first()
                
                if not order:
                    await websocket.send_json({
                        "error": "Orden no encontrada",
                        "order_number": order_number
                    })
                    break
                
                # Buscar tracking de entrega
                delivery = db.query(DeliveryTracking).filter(
                    DeliveryTracking.order_id == order.id
                ).first()
                
                if not delivery:
                    await websocket.send_json({
                        "error": "Entrega no asignada",
                        "order_number": order_number
                    })
                    break
                
                # Buscar conductor
                driver = db.query(Driver).filter(
                    Driver.id == delivery.driver_id
                ).first()
                
                if not driver:
                    await websocket.send_json({
                        "error": "Conductor no encontrado",
                        "order_number": order_number
                    })
                    break
                
                # Preparar datos de ubicación
                location_data = {
                    "order_number": order_number,
                    "driver_id": driver.id,
                    "driver_name": driver.user.full_name if driver.user else "Conductor",
                    "driver_phone": driver.phone,
                    "is_online": driver.is_online,
                    "is_delivering": driver.is_delivering,
                    "current_location": driver.current_location,
                    "last_update": driver.last_location_update.isoformat() if driver.last_location_update else None,
                    "delivery_status": delivery.status,
                    "estimated_arrival": delivery.estimated_arrival.isoformat() if delivery.estimated_arrival else None,
                    "distance_remaining": delivery.distance_remaining,
                    "vehicle_info": {
                        "brand": driver.vehicle.brand,
                        "model": driver.vehicle.model,
                        "plate": driver.vehicle.plate
                    } if driver.vehicle else None,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Enviar datos al cliente
                try:
                    await websocket.send_json(location_data)
                except Exception as send_error:
                    print(f"Error sending location data: {send_error}")
                    break
                
                # Verificar si la entrega está completada
                if delivery.status == "completed":
                    try:
                        await websocket.send_json({
                            "message": "Entrega completada",
                            "status": "completed",
                            "timestamp": datetime.utcnow().isoformat()
                        })
                    except Exception as send_error:
                        print(f"Error sending completion message: {send_error}")
                    break
                
            except Exception as e:
                try:
                    await websocket.send_json({
                        "error": f"Error interno: {str(e)}",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                except Exception as send_error:
                    print(f"Error sending error message: {send_error}")
                    break
            finally:
                db.close()
            
            # Esperar 5 segundos antes de la siguiente actualización
            await asyncio.sleep(5)
            
    except WebSocketDisconnect:
        pass
    finally:
        # Remover conexión de la lista activa
        if order_number in active_connections:
            active_connections[order_number].remove(websocket)
            if not active_connections[order_number]:
                del active_connections[order_number]

@tracking_router.websocket("/ws/driver/{driver_id}")
async def websocket_driver_location(websocket: WebSocket, driver_id: int):
    """
    WebSocket para que el conductor envíe su ubicación en tiempo real
    - Conductor se conecta con su ID
    - Envía ubicación cada 30 segundos
    - Backend actualiza base de datos y notifica a clientes
    """
    await websocket.accept()
    
    try:
        while True:
            # Recibir datos de ubicación del conductor
            data = await websocket.receive_json()
            
            # Validar datos recibidos
            if not all(key in data for key in ["latitude", "longitude"]):
                try:
                    await websocket.send_json({
                        "error": "Datos de ubicación incompletos",
                        "required": ["latitude", "longitude"]
                    })
                except Exception as send_error:
                    print(f"Error sending validation error: {send_error}")
                    break
                continue
            
            # Actualizar ubicación en base de datos
            db = next(get_db())
            try:
                # Buscar conductor
                driver = db.query(Driver).filter(Driver.id == driver_id).first()
                if not driver:
                    try:
                        await websocket.send_json({
                            "error": "Conductor no encontrado"
                        })
                    except Exception as send_error:
                        print(f"Error sending driver not found: {send_error}")
                        break
                    continue
                
                # Actualizar ubicación del conductor
                driver.current_location = {
                    "lat": data["latitude"],
                    "lng": data["longitude"],
                    "accuracy": data.get("accuracy", 0),
                    "speed": data.get("speed", 0),
                    "heading": data.get("heading", 0)
                }
                driver.last_location_update = datetime.utcnow()
                
                # Crear registro de ubicación
                location_update = LocationUpdate(
                    driver_id=driver_id,
                    latitude=data["latitude"],
                    longitude=data["longitude"],
                    accuracy=data.get("accuracy"),
                    speed=data.get("speed"),
                    heading=data.get("heading")
                )
                db.add(location_update)
                
                # Actualizar distancia restante si hay entrega activa
                active_delivery = db.query(DeliveryTracking).filter(
                    DeliveryTracking.driver_id == driver_id,
                    DeliveryTracking.status.in_(["assigned", "started", "in_progress"])
                ).first()
                
                if active_delivery and active_delivery.delivery_coordinates:
                    # Calcular distancia restante
                    from features.tracking.services import LocationService
                    distance = LocationService._calculate_distance(
                        data["latitude"], data["longitude"],
                        active_delivery.delivery_coordinates["lat"],
                        active_delivery.delivery_coordinates["lng"]
                    )
                    active_delivery.distance_remaining = distance
                    active_delivery.last_location_update = datetime.utcnow()
                
                db.commit()
                
                # Notificar a clientes conectados
                await notify_clients_about_location_update(driver_id, driver.current_location)
                
                # Confirmar recepción al conductor
                try:
                    await websocket.send_json({
                        "success": True,
                        "message": "Ubicación actualizada",
                        "timestamp": datetime.utcnow().isoformat(),
                        "location": driver.current_location
                    })
                except Exception as send_error:
                    print(f"Error sending location confirmation: {send_error}")
                    break
                
            except Exception as e:
                db.rollback()
                try:
                    await websocket.send_json({
                        "error": f"Error actualizando ubicación: {str(e)}"
                    })
                except Exception as send_error:
                    print(f"Error sending database error: {send_error}")
                    break
            finally:
                db.close()
            
            # Esperar 30 segundos antes de la siguiente actualización
            await asyncio.sleep(30)
            
    except WebSocketDisconnect:
        pass

async def notify_clients_about_location_update(driver_id: int, location_data: dict):
    """
    Notificar a todos los clientes conectados sobre actualización de ubicación
    """
    # Buscar órdenes activas de este conductor
    db = next(get_db())
    try:
        active_deliveries = db.query(DeliveryTracking).filter(
            DeliveryTracking.driver_id == driver_id,
            DeliveryTracking.status.in_(["assigned", "started", "in_progress"])
        ).all()
        
        for delivery in active_deliveries:
            order_number = delivery.order.woocommerce_order_id if delivery.order else None
            if order_number and order_number in active_connections:
                # Enviar actualización a todos los clientes conectados a esta orden
                for websocket in active_connections[order_number]:
                    try:
                        await websocket.send_json({
                            "type": "location_update",
                            "driver_id": driver_id,
                            "location": location_data,
                            "timestamp": datetime.utcnow().isoformat()
                        })
                    except:
                        # Remover conexión si falla
                        active_connections[order_number].remove(websocket)
    finally:
        db.close()

@tracking_router.get("/ws/status")
async def get_websocket_status():
    """
    Obtener estado de las conexiones WebSocket activas
    """
    return {
        "active_connections": len(active_connections),
        "orders_tracking": list(active_connections.keys()),
        "total_clients": sum(len(clients) for clients in active_connections.values())
    }
