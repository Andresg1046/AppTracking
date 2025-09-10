"""
Servicios para el módulo de vehículos
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Tuple
from datetime import datetime
import base64
from features.vehicles.models import Vehicle
from features.vehicles.schemas import VehicleCreate, VehicleUpdate, VehicleAssign
from features.users.models import User


class VehicleService:
    """Servicio para operaciones de vehículos"""

    @staticmethod
    def create_vehicle(vehicle_data: VehicleCreate, created_by: int, db: Session) -> Vehicle:
        """Crear un nuevo vehículo"""
        # Verificar que la placa no exista
        existing_vehicle = db.query(Vehicle).filter(Vehicle.plate == vehicle_data.plate).first()
        if existing_vehicle:
            raise ValueError(f"Ya existe un vehículo con la placa {vehicle_data.plate}")

        # Verificar que el usuario asignado existe (si se proporciona)
        if vehicle_data.assigned_user_id:
            assigned_user = db.query(User).filter(User.id == vehicle_data.assigned_user_id).first()
            if not assigned_user:
                raise ValueError(f"Usuario con ID {vehicle_data.assigned_user_id} no encontrado")

        # Verificar que quien asigna existe (si se proporciona)
        if vehicle_data.assigned_by:
            assigned_by_user = db.query(User).filter(User.id == vehicle_data.assigned_by).first()
            if not assigned_by_user:
                raise ValueError(f"Usuario con ID {vehicle_data.assigned_by} no encontrado")

        # Crear el vehículo
        vehicle_dict = vehicle_data.dict()
        vehicle_dict['created_by'] = created_by
        
        # Si se asigna un usuario, establecer fecha de asignación
        if vehicle_data.assigned_user_id:
            vehicle_dict['assigned_at'] = datetime.utcnow()

        # Convertir foto de base64 a bytes (si se proporciona)
        if 'photo' in vehicle_dict and vehicle_dict['photo']:
            try:
                vehicle_dict['photo_data'] = base64.b64decode(vehicle_dict['photo'])
                vehicle_dict['photo_content_type'] = 'image/jpeg'  # Por defecto
            except Exception:
                # Si no es base64 válido, ignorar la foto
                pass
        
        # Siempre remover el campo photo del dict si existe
        if 'photo' in vehicle_dict:
            del vehicle_dict['photo']

        vehicle = Vehicle(**vehicle_dict)
        db.add(vehicle)
        db.commit()
        db.refresh(vehicle)
        return vehicle

    @staticmethod
    def get_vehicle_by_id(vehicle_id: int, db: Session) -> Optional[Vehicle]:
        """Obtener un vehículo por ID"""
        return db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()

    @staticmethod
    def get_vehicle_by_plate(plate: str, db: Session) -> Optional[Vehicle]:
        """Obtener un vehículo por placa"""
        return db.query(Vehicle).filter(Vehicle.plate == plate.upper()).first()

    @staticmethod
    def get_vehicles(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None,
        status: Optional[str] = None,
        assigned_user_id: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[Vehicle], int]:
        """Obtener lista de vehículos con filtros"""
        query = db.query(Vehicle)

        # Filtros
        if search:
            search_filter = or_(
                Vehicle.plate.ilike(f"%{search}%"),
                Vehicle.brand.ilike(f"%{search}%"),
                Vehicle.model.ilike(f"%{search}%"),
                Vehicle.color.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)

        if status:
            query = query.filter(Vehicle.status == status)

        if assigned_user_id:
            query = query.filter(Vehicle.assigned_user_id == assigned_user_id)

        if is_active is not None:
            query = query.filter(Vehicle.is_active == is_active)

        # Contar total
        total = query.count()

        # Aplicar paginación y ordenar
        vehicles = query.order_by(Vehicle.created_at.desc()).offset(skip).limit(limit).all()

        return vehicles, total

    @staticmethod
    def update_vehicle(vehicle_id: int, vehicle_data: VehicleUpdate, updated_by: int, db: Session) -> Optional[Vehicle]:
        """Actualizar un vehículo"""
        vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        if not vehicle:
            return None

        # Verificar que la nueva placa no exista (si se está cambiando)
        if vehicle_data.plate and vehicle_data.plate != vehicle.plate:
            existing_vehicle = db.query(Vehicle).filter(
                and_(Vehicle.plate == vehicle_data.plate, Vehicle.id != vehicle_id)
            ).first()
            if existing_vehicle:
                raise ValueError(f"Ya existe un vehículo con la placa {vehicle_data.plate}")

        # Verificar usuarios si se proporcionan
        if vehicle_data.assigned_user_id:
            assigned_user = db.query(User).filter(User.id == vehicle_data.assigned_user_id).first()
            if not assigned_user:
                raise ValueError(f"Usuario con ID {vehicle_data.assigned_user_id} no encontrado")

        # Actualizar campos
        update_data = vehicle_data.dict(exclude_unset=True)
        
        # Convertir foto de base64 a bytes si se proporciona
        if 'photo' in update_data and update_data['photo']:
            try:
                update_data['photo_data'] = base64.b64decode(update_data['photo'])
                update_data['photo_content_type'] = 'image/jpeg'  # Por defecto
            except Exception:
                # Si no es base64 válido, ignorar la foto
                pass
        
        # Siempre remover el campo photo del dict si existe
        if 'photo' in update_data:
            del update_data['photo']
        
        for field, value in update_data.items():
            setattr(vehicle, field, value)

        # Si se asigna un nuevo usuario, actualizar fecha de asignación
        if vehicle_data.assigned_user_id and vehicle_data.assigned_user_id != vehicle.assigned_user_id:
            vehicle.assigned_at = datetime.utcnow()
            vehicle.assigned_by = updated_by

        vehicle.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(vehicle)
        return vehicle

    @staticmethod
    def assign_vehicle(vehicle_id: int, assign_data: VehicleAssign, db: Session) -> Optional[Vehicle]:
        """Asignar un vehículo a un usuario"""
        vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        if not vehicle:
            return None

        # Verificar que el usuario asignado existe
        assigned_user = db.query(User).filter(User.id == assign_data.assigned_user_id).first()
        if not assigned_user:
            raise ValueError(f"Usuario con ID {assign_data.assigned_user_id} no encontrado")

        # Verificar que quien asigna existe
        assigned_by_user = db.query(User).filter(User.id == assign_data.assigned_by).first()
        if not assigned_by_user:
            raise ValueError(f"Usuario con ID {assign_data.assigned_by} no encontrado")

        # Asignar vehículo
        vehicle.assigned_user_id = assign_data.assigned_user_id
        vehicle.assigned_by = assign_data.assigned_by
        vehicle.assigned_at = datetime.utcnow()
        vehicle.updated_at = datetime.utcnow()

        if assign_data.notes:
            vehicle.notes = assign_data.notes

        db.commit()
        db.refresh(vehicle)
        return vehicle

    @staticmethod
    def unassign_vehicle(vehicle_id: int, db: Session) -> Optional[Vehicle]:
        """Desasignar un vehículo"""
        vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        if not vehicle:
            return None

        vehicle.assigned_user_id = None
        vehicle.assigned_by = None
        vehicle.assigned_at = None
        vehicle.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(vehicle)
        return vehicle

    @staticmethod
    def delete_vehicle(vehicle_id: int, db: Session) -> bool:
        """Eliminar un vehículo (soft delete)"""
        vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        if not vehicle:
            return False

        vehicle.is_active = False
        vehicle.updated_at = datetime.utcnow()
        db.commit()
        return True

    @staticmethod
    def get_vehicles_by_user(user_id: int, db: Session) -> List[Vehicle]:
        """Obtener vehículos asignados a un usuario"""
        return db.query(Vehicle).filter(
            and_(
                Vehicle.assigned_user_id == user_id,
                Vehicle.is_active == True
            )
        ).all()

    @staticmethod
    def get_vehicle_stats(db: Session) -> dict:
        """Obtener estadísticas de vehículos"""
        total_vehicles = db.query(Vehicle).filter(Vehicle.is_active == True).count()
        active_vehicles = db.query(Vehicle).filter(
            and_(Vehicle.is_active == True, Vehicle.status == "active")
        ).count()
        assigned_vehicles = db.query(Vehicle).filter(
            and_(Vehicle.is_active == True, Vehicle.assigned_user_id.isnot(None))
        ).count()
        unassigned_vehicles = total_vehicles - assigned_vehicles

        return {
            "total_vehicles": total_vehicles,
            "active_vehicles": active_vehicles,
            "assigned_vehicles": assigned_vehicles,
            "unassigned_vehicles": unassigned_vehicles
        }

    @staticmethod
    def convert_vehicle_to_response(vehicle: Vehicle) -> dict:
        """Convertir vehículo de la BD a formato de respuesta con foto en base64"""
        vehicle_dict = {
            "id": vehicle.id,
            "brand": vehicle.brand,
            "model": vehicle.model,
            "year": vehicle.year,
            "color": vehicle.color,
            "plate": vehicle.plate,
            "state": vehicle.state,
            "photo_content_type": vehicle.photo_content_type,
            "status": vehicle.status,
            "assigned_user_id": vehicle.assigned_user_id,
            "assigned_at": vehicle.assigned_at,
            "assigned_by": vehicle.assigned_by,
            "is_active": vehicle.is_active,
            "notes": vehicle.notes,
            "created_by": vehicle.created_by,
            "created_at": vehicle.created_at,
            "updated_at": vehicle.updated_at,
            "photo": None
        }

        # Convertir foto de bytes a base64
        if vehicle.photo_data:
            vehicle_dict["photo"] = base64.b64encode(vehicle.photo_data).decode('utf-8')

        # Agregar información de usuarios si están disponibles
        if vehicle.assigned_user:
            vehicle_dict["assigned_user_name"] = vehicle.assigned_user.full_name
            vehicle_dict["assigned_user_email"] = vehicle.assigned_user.email

        if vehicle.assigned_by_user:
            vehicle_dict["assigned_by_name"] = vehicle.assigned_by_user.full_name

        if vehicle.creator:
            vehicle_dict["creator_name"] = vehicle.creator.full_name

        return vehicle_dict
