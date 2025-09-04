from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, User, Vehicle
from auth import get_password_hash

def init_db():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if admin user already exists
        admin_user = db.query(User).filter(User.email == "admin@company.com").first()
        if not admin_user:
            # Create admin user
            admin_user = User(
                email="admin@company.com",
                hashed_password=get_password_hash("admin123"),
                full_name="Administrador",
                role="admin",
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print("Admin user created: admin@company.com / admin123")
        
        # Check if driver users exist
        driver1 = db.query(User).filter(User.email == "driver1@company.com").first()
        if not driver1:
            # Create driver 1
            driver1 = User(
                email="driver1@company.com",
                hashed_password=get_password_hash("driver123"),
                full_name="Juan Pérez",
                role="driver",
                is_active=True
            )
            db.add(driver1)
            db.commit()
            db.refresh(driver1)
            print("Driver 1 created: driver1@company.com / driver123")
        
        driver2 = db.query(User).filter(User.email == "driver2@company.com").first()
        if not driver2:
            # Create driver 2
            driver2 = User(
                email="driver2@company.com",
                hashed_password=get_password_hash("driver123"),
                full_name="María García",
                role="driver",
                is_active=True
            )
            db.add(driver2)
            db.commit()
            db.refresh(driver2)
            print("Driver 2 created: driver2@company.com / driver123")
        
        # Create vehicles
        vehicle1 = db.query(Vehicle).filter(Vehicle.plate_number == "ABC123").first()
        if not vehicle1:
            vehicle1 = Vehicle(
                plate_number="ABC123",
                model="Toyota Hilux",
                brand="Toyota",
                year=2022,
                driver_id=driver1.id if driver1 else None,
                is_active=True
            )
            db.add(vehicle1)
            print("Vehicle 1 created: ABC123")
        
        vehicle2 = db.query(Vehicle).filter(Vehicle.plate_number == "XYZ789").first()
        if not vehicle2:
            vehicle2 = Vehicle(
                plate_number="XYZ789",
                model="Ford Ranger",
                brand="Ford",
                year=2021,
                driver_id=driver2.id if driver2 else None,
                is_active=True
            )
            db.add(vehicle2)
            print("Vehicle 2 created: XYZ789")
        
        db.commit()
        print("\nDatabase initialized successfully!")
        print("\nDefault users:")
        print("- Admin: admin@company.com / admin123")
        print("- Driver 1: driver1@company.com / driver123")
        print("- Driver 2: driver2@company.com / driver123")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
