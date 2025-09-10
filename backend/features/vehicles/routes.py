"""
Rutas para el módulo de vehículos
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import base64
from core.database import get_db
from core.security import get_current_user
from features.users.models import User
from features.vehicles.schemas import (
    VehicleCreate, VehicleUpdate, VehicleResponse, VehicleListResponse,
    VehicleAssign, VehicleLookupRequest, VehicleLookupResponse
)
from features.vehicles.services import VehicleService

vehicles_router = APIRouter()


@vehicles_router.post("/", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    vehicle: VehicleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear un nuevo vehículo"""
    try:
        created_vehicle = VehicleService.create_vehicle(vehicle, current_user.id, db)
        
        # Obtener información adicional para la respuesta
        response_data = VehicleService.get_vehicle_by_id(created_vehicle.id, db)
        return response_data
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print(f"Error creando vehículo: {e}")  # Para debug
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error interno del servidor: {str(e)}")


@vehicles_router.get("/", response_model=VehicleListResponse)
def get_vehicles(
    page: int = Query(1, ge=1, description="Número de página"),
    per_page: int = Query(10, ge=1, le=100, description="Elementos por página"),
    search: Optional[str] = Query(None, description="Término de búsqueda"),
    status: Optional[str] = Query(None, description="Filtrar por estado"),
    assigned_user_id: Optional[int] = Query(None, description="Filtrar por usuario asignado"),
    is_active: Optional[bool] = Query(True, description="Filtrar por estado activo"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener lista de vehículos con filtros y paginación"""
    skip = (page - 1) * per_page
    
    vehicles, total = VehicleService.get_vehicles(
        db=db,
        skip=skip,
        limit=per_page,
        search=search,
        status=status,
        assigned_user_id=assigned_user_id,
        is_active=is_active
    )
    
    total_pages = (total + per_page - 1) // per_page
    
    return VehicleListResponse(
        vehicles=vehicles,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


@vehicles_router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(
    vehicle_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener un vehículo por ID"""
    vehicle = VehicleService.get_vehicle_by_id(vehicle_id, db)
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado")
    
    return vehicle


@vehicles_router.get("/plate/{plate}", response_model=VehicleResponse)
def get_vehicle_by_plate(
    plate: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener un vehículo por placa"""
    vehicle = VehicleService.get_vehicle_by_plate(plate, db)
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado")
    
    return vehicle


@vehicles_router.put("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(
    vehicle_id: int,
    vehicle_update: VehicleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar un vehículo"""
    try:
        vehicle = VehicleService.update_vehicle(vehicle_id, vehicle_update, current_user.id, db)
        if not vehicle:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado")
        
        return vehicle
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")


@vehicles_router.post("/{vehicle_id}/assign", response_model=VehicleResponse)
def assign_vehicle(
    vehicle_id: int,
    assign_data: VehicleAssign,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Asignar un vehículo a un usuario"""
    try:
        vehicle = VehicleService.assign_vehicle(vehicle_id, assign_data, db)
        if not vehicle:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado")
        
        return vehicle
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")


@vehicles_router.post("/{vehicle_id}/unassign", response_model=VehicleResponse)
def unassign_vehicle(
    vehicle_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Desasignar un vehículo"""
    vehicle = VehicleService.unassign_vehicle(vehicle_id, db)
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado")
    
    return vehicle


@vehicles_router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(
    vehicle_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar un vehículo (soft delete)"""
    success = VehicleService.delete_vehicle(vehicle_id, db)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado")


@vehicles_router.get("/user/{user_id}/vehicles", response_model=List[VehicleResponse])
def get_vehicles_by_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener vehículos asignados a un usuario específico"""
    vehicles = VehicleService.get_vehicles_by_user(user_id, db)
    return vehicles


@vehicles_router.get("/stats/summary")
def get_vehicle_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener estadísticas de vehículos"""
    stats = VehicleService.get_vehicle_stats(db)
    return stats


@vehicles_router.post("/lookup", response_model=VehicleLookupResponse)
def lookup_vehicle(
    lookup_request: VehicleLookupRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Buscar un vehículo por placa y estado"""
    vehicle = VehicleService.get_vehicle_by_plate(lookup_request.plate, db)
    
    if vehicle:
        return VehicleLookupResponse(
            found=True,
            vehicle=vehicle,
            message="Vehículo encontrado en la base de datos local"
        )
    else:
        return VehicleLookupResponse(
            found=False,
            vehicle=None,
            message=f"No se encontró un vehículo con la placa {lookup_request.plate} en el estado {lookup_request.state}"
        )


@vehicles_router.post("/{vehicle_id}/photo", response_model=VehicleResponse)
async def upload_vehicle_photo(
    vehicle_id: int,
    photo: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Subir foto de un vehículo"""
    # Verificar que el vehículo existe
    vehicle = VehicleService.get_vehicle_by_id(vehicle_id, db)
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado")
    
    # Verificar que es una imagen
    if not photo.content_type or not photo.content_type.startswith('image/'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo debe ser una imagen")
    
    # Leer la imagen y convertir a base64
    try:
        photo_data = await photo.read()
        photo_base64 = base64.b64encode(photo_data).decode('utf-8')
        
        # Actualizar el vehículo con la nueva foto
        vehicle.photo_data = photo_data
        vehicle.photo_content_type = photo.content_type
        vehicle.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(vehicle)
        
        return vehicle
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al procesar la imagen")
