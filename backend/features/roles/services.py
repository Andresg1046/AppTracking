from sqlalchemy.orm import Session
from features.roles.models import Role

class RoleService:
    @staticmethod
    def get_all_roles(db: Session) -> list[Role]:
        """Obtiene todos los roles"""
        return db.query(Role).all()
    
    @staticmethod
    def get_role_by_name(name: str, db: Session) -> Role:
        """Obtiene un rol por nombre"""
        return db.query(Role).filter(Role.name == name).first()
    
    @staticmethod
    def get_role_by_id(role_id: int, db: Session) -> Role:
        """Obtiene un rol por ID"""
        return db.query(Role).filter(Role.id == role_id).first()
    
    @staticmethod
    def create_role(role_data: dict, db: Session) -> Role:
        """Crea un nuevo rol"""
        from sqlalchemy.exc import IntegrityError
        
        # Verificar que el nombre no existe
        existing_role = db.query(Role).filter(Role.name == role_data["name"]).first()
        if existing_role:
            raise ValueError("Role name already exists")
        
        db_role = Role(
            name=role_data["name"],
            description=role_data.get("description")
        )
        
        try:
            db.add(db_role)
            db.commit()
            db.refresh(db_role)
            return db_role
        except IntegrityError:
            db.rollback()
            raise ValueError("Role name already exists")
    
    @staticmethod
    def update_role(role_id: int, role_data: dict, db: Session) -> Role:
        """Actualiza un rol"""
        from sqlalchemy.exc import IntegrityError
        
        db_role = db.query(Role).filter(Role.id == role_id).first()
        if not db_role:
            raise ValueError("Role not found")
        
        # Verificar que el nombre no existe si se está cambiando
        if "name" in role_data and role_data["name"] is not None:
            existing_role = db.query(Role).filter(
                Role.name == role_data["name"],
                Role.id != role_id
            ).first()
            if existing_role:
                raise ValueError("Role name already exists")
        
        # Actualizar campos
        for field, value in role_data.items():
            if value is not None and hasattr(db_role, field):
                setattr(db_role, field, value)
        
        try:
            db.commit()
            db.refresh(db_role)
            return db_role
        except IntegrityError:
            db.rollback()
            raise ValueError("Role name already exists")
    
    @staticmethod
    def delete_role(role_id: int, db: Session) -> bool:
        """Elimina un rol"""
        from features.users.models import User
        
        db_role = db.query(Role).filter(Role.id == role_id).first()
        if not db_role:
            raise ValueError("Role not found")
        
        # Verificar que no hay usuarios con este rol
        users_with_role = db.query(User).filter(User.role_id == role_id).count()
        if users_with_role > 0:
            raise ValueError(f"Cannot delete role. {users_with_role} users are assigned to this role")
        
        # No permitir eliminar roles básicos
        if db_role.name in ["admin", "driver"]:
            raise ValueError("Cannot delete basic roles (admin, driver)")
        
        db.delete(db_role)
        db.commit()
        return True