from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    phone = Column(String)
    role_id = Column(Integer, ForeignKey("roles.id"))
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relaciones
    role = relationship("Role", back_populates="users")
    sessions = relationship("UserSession", back_populates="user")
    
    # Relaciones con vehículos
    assigned_vehicles = relationship("Vehicle", foreign_keys="Vehicle.assigned_user_id", back_populates="assigned_user")
    vehicles_assigned_by_me = relationship("Vehicle", foreign_keys="Vehicle.assigned_by", back_populates="assigned_by_user")
    vehicles_created = relationship("Vehicle", foreign_keys="Vehicle.created_by", back_populates="creator")
    
    # Relación con perfil de conductor
    driver_profile = relationship("Driver", back_populates="user", uselist=False)