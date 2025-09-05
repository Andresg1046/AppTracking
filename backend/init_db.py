from database import engine, SessionLocal
from models import Base, Role

# Create tables
Base.metadata.create_all(bind=engine)

# Create default roles
db = SessionLocal()

try:
    # Crear rol admin
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    if not admin_role:
        admin_role = Role(name="admin", description="Administrator role")
        db.add(admin_role)
        print("Admin role created")

    # Crear rol driver
    driver_role = db.query(Role).filter(Role.name == "driver").first()
    if not driver_role:
        driver_role = Role(name="driver", description="Driver role")
        db.add(driver_role)
        print("Driver role created")

    db.commit()
    print("\nDatabase initialized successfully!")
    print("Default roles created: admin, driver")
    print("The first user to register will automatically become an admin.")
    print("All subsequent users will be drivers.")

except Exception as e:
    print(f"Error initializing database: {e}")
    db.rollback()
finally:
    db.close()