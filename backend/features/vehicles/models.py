"""
Modelos para el módulo de vehículos
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Date, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base


class Vehicle(Base):
    """Modelo para vehículos"""
    __tablename__ = "vehicles"

    # Campos básicos
    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String(50), nullable=False, index=True)  # Marca
    model = Column(String(50), nullable=False, index=True)  # Modelo
    year = Column(Integer, nullable=False, index=True)      # Año
    color = Column(String(30))                              # Color
    plate = Column(String(20), unique=True, nullable=False, index=True)  # Placa
    state = Column(String(10), nullable=False)              # Estado (FL, CA, etc.)
    photo_data = Column(LargeBinary)                        # Datos de la foto como bytes
    photo_content_type = Column(String(50))                 # Tipo de contenido (image/jpeg, image/png)
    
    # Asignación
    assigned_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Usuario asignado
    assigned_at = Column(DateTime, nullable=True)           # Fecha de asignación
    assigned_by = Column(Integer, ForeignKey("users.id"), nullable=True)      # Asignado por
    status = Column(String(20), default="active", nullable=False)  # Estatus
    
    # Sistema
    is_active = Column(Boolean, default=True, nullable=False)
    notes = Column(Text)                                    # Notas adicionales
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relaciones
    assigned_user = relationship("User", foreign_keys=[assigned_user_id], back_populates="assigned_vehicles")
    assigned_by_user = relationship("User", foreign_keys=[assigned_by], back_populates="vehicles_assigned_by_me")
    creator = relationship("User", foreign_keys=[created_by], back_populates="vehicles_created")
    
    # Relación con conductor asignado
    assigned_driver = relationship("Driver", back_populates="vehicle", uselist=False)

    def __repr__(self):
        return f"<Vehicle(id={self.id}, plate='{self.plate}', brand='{self.brand}', model='{self.model}')>"
