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
