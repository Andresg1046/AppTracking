from sqlalchemy.orm import Session
from features.users.models import User
from features.roles.models import Role
from core.security import get_password_hash

class UserService:
    @staticmethod
    def create_user(user_data: dict, db: Session) -> User:
        """Crea un nuevo usuario"""
        # Verificar si es el primer usuario (será admin)
        user_count = db.query(User).count()
        
        if user_count == 0:
            # Primer usuario - asignar rol admin
            admin_role = db.query(Role).filter(Role.name == "admin").first()
            if not admin_role:
                admin_role = Role(name="admin", description="Administrator role")
                db.add(admin_role)
                db.commit()
            role_id = admin_role.id
        else:
            # Usuarios siguientes - asignar rol driver
            driver_role = db.query(Role).filter(Role.name == "driver").first()
            if not driver_role:
                driver_role = Role(name="driver", description="Driver role")
                db.add(driver_role)
                db.commit()
            role_id = driver_role.id
        
        hashed_password = get_password_hash(user_data["password"])
        db_user = User(
            email=user_data["email"],
            hashed_password=hashed_password,
            full_name=user_data["full_name"],
            phone=user_data["phone"],
            role_id=role_id
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def get_user_by_email(email: str, db: Session) -> User:
        """Obtiene un usuario por email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_all_users(db: Session) -> list[User]:
        """Obtiene todos los usuarios"""
        return db.query(User).all()
