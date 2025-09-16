"""
Servicios para el sistema de tracking
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
import logging
import math

from features.tracking.models import Driver, DeliveryTracking, LocationUpdate, DriverSession
from features.users.models import User
from features.vehicles.models import Vehicle
from features.ecommerce.models import Order
from features.tracking.schemas import (
    DriverActivateRequest, DriverUpdateRequest, LocationUpdateRequest,
    DeliveryTrackingCreate, DeliveryStatusUpdate
)

logger = logging.getLogger(__name__)

class DriverService:
    """Servicio para gestión de conductores"""
    
    @staticmethod
    def activate_driver(user_id: int, driver_data: DriverActivateRequest, db: Session) -> Optional[Driver]:
        """Activar usuario como conductor"""
        try:
            # Verificar que el usuario existe y tiene rol driver
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError("Usuario no encontrado")
            
            if not user.role or user.role.name != "driver":
                raise ValueError("El usuario debe tener rol 'driver' para activarse como conductor")
            
            # Verificar que no sea conductor ya activo
            existing_driver = db.query(Driver).filter(Driver.user_id == user_id).first()
            if existing_driver:
                raise ValueError("El usuario ya es conductor activo")
            
            # Crear perfil de conductor
            driver = Driver(
                user_id=user_id,
                vehicle_id=driver_data.vehicle_id,
                driver_license=driver_data.driver_license,
                phone=driver_data.phone or user.phone,
                notes=driver_data.notes,
                location_update_interval=driver_data.location_update_interval,
                auto_location_sharing=driver_data.auto_location_sharing
            )
            
            db.add(driver)
            db.commit()
            db.refresh(driver)
            
            logger.info(f"Conductor activado: User ID {user_id}, Driver ID {driver.id}")
            return driver
            
        except Exception as e:
            logger.error(f"Error activando conductor: {str(e)}")
            db.rollback()
            raise
    
    @staticmethod
    def get_driver_by_user_id(user_id: int, db: Session) -> Optional[Driver]:
        """Obtener conductor por ID de usuario"""
        return db.query(Driver).filter(Driver.user_id == user_id).first()
    
    @staticmethod
    def get_driver_by_id(driver_id: int, db: Session) -> Optional[Driver]:
        """Obtener conductor por ID"""
        return db.query(Driver).filter(Driver.id == driver_id).first()
    
    @staticmethod
    def update_driver_profile(driver_id: int, update_data: DriverUpdateRequest, db: Session) -> Optional[Driver]:
        """Actualizar perfil de conductor"""
        try:
            driver = db.query(Driver).filter(Driver.id == driver_id).first()
            if not driver:
                return None
            
            # Actualizar campos proporcionados
            if update_data.vehicle_id is not None:
                driver.vehicle_id = update_data.vehicle_id
            if update_data.driver_license is not None:
                driver.driver_license = update_data.driver_license
            if update_data.phone is not None:
                driver.phone = update_data.phone
            if update_data.notes is not None:
                driver.notes = update_data.notes
            if update_data.location_update_interval is not None:
                driver.location_update_interval = update_data.location_update_interval
            if update_data.auto_location_sharing is not None:
                driver.auto_location_sharing = update_data.auto_location_sharing
            
            driver.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(driver)
            
            return driver
            
        except Exception as e:
            logger.error(f"Error actualizando conductor: {str(e)}")
            db.rollback()
            raise
    
    @staticmethod
    def update_driver_status(driver_id: int, is_online: Optional[bool] = None, 
                           is_available: Optional[bool] = None, db: Session = None) -> Optional[Driver]:
        """Actualizar estado del conductor"""
        try:
            driver = db.query(Driver).filter(Driver.id == driver_id).first()
            if not driver:
                return None
            
            if is_online is not None:
                driver.is_online = is_online
            if is_available is not None:
                driver.is_available = is_available
            
            driver.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(driver)
            
            return driver
            
        except Exception as e:
            logger.error(f"Error actualizando estado del conductor: {str(e)}")
            db.rollback()
            raise
    
    @staticmethod
    def get_all_drivers(db: Session, skip: int = 0, limit: int = 100, 
                       online_only: bool = False, available_only: bool = False) -> Tuple[List[Driver], int]:
        """Obtener todos los conductores con filtros"""
        query = db.query(Driver)
        
        if online_only:
            query = query.filter(Driver.is_online == True)
        if available_only:
            query = query.filter(Driver.is_available == True)
        
        total = query.count()
        drivers = query.offset(skip).limit(limit).all()
        
        return drivers, total
    
    @staticmethod
    def get_driver_stats(driver_id: int, db: Session) -> Dict[str, Any]:
        """Obtener estadísticas del conductor"""
        try:
            driver = db.query(Driver).filter(Driver.id == driver_id).first()
            if not driver:
                return {}
            
            # Estadísticas de entregas
            total_deliveries = db.query(DeliveryTracking).filter(DeliveryTracking.driver_id == driver_id).count()
            completed_deliveries = db.query(DeliveryTracking).filter(
                and_(DeliveryTracking.driver_id == driver_id, DeliveryTracking.status == "completed")
            ).count()
            failed_deliveries = db.query(DeliveryTracking).filter(
                and_(DeliveryTracking.driver_id == driver_id, DeliveryTracking.status == "failed")
            ).count()
            
            success_rate = (completed_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0
            
            # Entregas de los últimos 30 días
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_deliveries = db.query(DeliveryTracking).filter(
                and_(
                    DeliveryTracking.driver_id == driver_id,
                    DeliveryTracking.assigned_at >= thirty_days_ago
                )
            ).count()
            
            return {
                "total_deliveries": total_deliveries,
                "completed_deliveries": completed_deliveries,
                "failed_deliveries": failed_deliveries,
                "success_rate": round(success_rate, 2),
                "recent_deliveries_30_days": recent_deliveries
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas del conductor: {str(e)}")
            return {}

class LocationService:
    """Servicio para gestión de ubicaciones"""
    
    @staticmethod
    def update_driver_location(driver_id: int, location_data: LocationUpdateRequest, 
                              delivery_id: Optional[int] = None, db: Session = None) -> Dict[str, Any]:
        """Actualizar ubicación del conductor"""
        try:
            driver = db.query(Driver).filter(Driver.id == driver_id).first()
            if not driver:
                return {"success": False, "message": "Conductor no encontrado"}
            
            # Crear registro de actualización de ubicación
            location_update = LocationUpdate(
                driver_id=driver_id,
                delivery_id=delivery_id,
                latitude=location_data.latitude,
                longitude=location_data.longitude,
                accuracy=location_data.accuracy,
                speed=location_data.speed,
                heading=location_data.heading
            )
            
            db.add(location_update)
            
            # Actualizar ubicación actual del conductor
            driver.current_location = {
                "lat": location_data.latitude,
                "lng": location_data.longitude,
                "accuracy": location_data.accuracy,
                "speed": location_data.speed,
                "heading": location_data.heading,
                "timestamp": datetime.utcnow().isoformat()
            }
            driver.last_location_update = datetime.utcnow()
            
            db.commit()
            
            # Calcular distancia a destino si hay entrega activa
            distance_from_destination = None
            estimated_arrival = None
            
            if delivery_id:
                delivery = db.query(DeliveryTracking).filter(DeliveryTracking.id == delivery_id).first()
                if delivery and delivery.delivery_coordinates:
                    dest_lat = delivery.delivery_coordinates.get("lat")
                    dest_lng = delivery.delivery_coordinates.get("lng")
                    if dest_lat and dest_lng:
                        distance_from_destination = LocationService._calculate_distance(
                            location_data.latitude, location_data.longitude,
                            dest_lat, dest_lng
                        )
                        
                        # Estimar tiempo de llegada basado en distancia y velocidad
                        if location_data.speed and location_data.speed > 0:
                            estimated_arrival = datetime.utcnow() + timedelta(
                                hours=distance_from_destination / location_data.speed
                            )
            
            return {
                "success": True,
                "message": "Ubicación actualizada",
                "timestamp": datetime.utcnow(),
                "location": {
                    "lat": location_data.latitude,
                    "lng": location_data.longitude,
                    "accuracy": location_data.accuracy,
                    "speed": location_data.speed,
                    "heading": location_data.heading
                },
                "distance_from_destination": distance_from_destination,
                "estimated_arrival": estimated_arrival
            }
            
        except Exception as e:
            logger.error(f"Error actualizando ubicación: {str(e)}")
            db.rollback()
            return {"success": False, "message": f"Error: {str(e)}"}
    
    @staticmethod
    def get_driver_location_history(driver_id: int, hours: int = 24, db: Session = None) -> List[Dict[str, Any]]:
        """Obtener historial de ubicaciones del conductor"""
        try:
            since = datetime.utcnow() - timedelta(hours=hours)
            
            updates = db.query(LocationUpdate).filter(
                and_(
                    LocationUpdate.driver_id == driver_id,
                    LocationUpdate.timestamp >= since
                )
            ).order_by(LocationUpdate.timestamp.desc()).all()
            
            return [
                {
                    "latitude": update.latitude,
                    "longitude": update.longitude,
                    "accuracy": update.accuracy,
                    "speed": update.speed,
                    "heading": update.heading,
                    "timestamp": update.timestamp
                }
                for update in updates
            ]
            
        except Exception as e:
            logger.error(f"Error obteniendo historial de ubicaciones: {str(e)}")
            return []
    
    @staticmethod
    def _calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calcular distancia entre dos puntos en kilómetros (fórmula de Haversine)"""
        R = 6371  # Radio de la Tierra en kilómetros
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat/2) * math.sin(dlat/2) + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlon/2) * math.sin(dlon/2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        return round(distance, 2)

class DeliveryTrackingService:
    """Servicio para gestión de entregas"""
    
    @staticmethod
    def assign_delivery(delivery_data: DeliveryTrackingCreate, db: Session) -> Optional[DeliveryTracking]:
        """Asignar entrega a conductor"""
        try:
            # Verificar que la orden existe
            order = db.query(Order).filter(Order.id == delivery_data.order_id).first()
            if not order:
                raise ValueError("Orden no encontrada")
            
            # Verificar que el conductor existe y está disponible
            driver = db.query(Driver).filter(Driver.id == delivery_data.driver_id).first()
            if not driver:
                raise ValueError("Conductor no encontrado")
            
            if not driver.is_available:
                raise ValueError("Conductor no está disponible")
            
            # Verificar que no hay entrega activa para esta orden
            existing_delivery = db.query(DeliveryTracking).filter(
                and_(
                    DeliveryTracking.order_id == delivery_data.order_id,
                    DeliveryTracking.status.in_(["assigned", "started", "in_progress"])
                )
            ).first()
            
            if existing_delivery:
                raise ValueError("La orden ya tiene una entrega asignada")
            
            # Crear tracking de entrega
            delivery_tracking = DeliveryTracking(
                order_id=delivery_data.order_id,
                driver_id=delivery_data.driver_id,
                priority=delivery_data.priority.value,
                delivery_notes=delivery_data.delivery_notes,
                estimated_duration=delivery_data.estimated_duration,
                customer_name=order.customer_name,
                customer_phone=order.customer_phone,
                delivery_address=order.shipping_address
            )
            
            # Extraer coordenadas de la dirección de envío si está disponible
            if order.shipping_address:
                # Aquí podrías geocodificar la dirección para obtener coordenadas
                # Por ahora lo dejamos como None
                delivery_tracking.delivery_coordinates = None
            
            db.add(delivery_tracking)
            
            # Marcar conductor como ocupado
            driver.is_available = False
            driver.is_delivering = True
            
            db.commit()
            db.refresh(delivery_tracking)
            
            logger.info(f"Entrega asignada: Order ID {delivery_data.order_id}, Driver ID {delivery_data.driver_id}")
            return delivery_tracking
            
        except Exception as e:
            logger.error(f"Error asignando entrega: {str(e)}")
            db.rollback()
            raise
    
    @staticmethod
    def get_driver_deliveries(driver_id: int, db: Session, 
                             status_filter: Optional[str] = None) -> List[DeliveryTracking]:
        """Obtener entregas del conductor"""
        query = db.query(DeliveryTracking).filter(DeliveryTracking.driver_id == driver_id)
        
        if status_filter:
            query = query.filter(DeliveryTracking.status == status_filter)
        
        return query.order_by(desc(DeliveryTracking.assigned_at)).all()
    
    @staticmethod
    def update_delivery_status(delivery_id: int, status_update: DeliveryStatusUpdate, 
                              db: Session) -> Optional[DeliveryTracking]:
        """Actualizar estado de entrega"""
        try:
            delivery = db.query(DeliveryTracking).filter(DeliveryTracking.id == delivery_id).first()
            if not delivery:
                return None
            
            old_status = delivery.status
            delivery.status = status_update.status.value
            
            # Actualizar timestamps según el estado
            if status_update.status.value == "started" and not delivery.started_at:
                delivery.started_at = datetime.utcnow()
            elif status_update.status.value == "completed" and not delivery.completed_at:
                delivery.completed_at = datetime.utcnow()
                
                # Liberar conductor
                driver = db.query(Driver).filter(Driver.id == delivery.driver_id).first()
                if driver:
                    driver.is_available = True
                    driver.is_delivering = False
            
            if status_update.estimated_arrival:
                delivery.estimated_arrival = status_update.estimated_arrival
            
            if status_update.notes:
                delivery.delivery_notes = status_update.notes
            
            db.commit()
            db.refresh(delivery)
            
            logger.info(f"Estado de entrega actualizado: {old_status} -> {status_update.status.value}")
            return delivery
            
        except Exception as e:
            logger.error(f"Error actualizando estado de entrega: {str(e)}")
            db.rollback()
            raise
