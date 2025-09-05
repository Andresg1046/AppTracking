from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

from database import get_db, engine
from models import Base, User, Role
from schemas import UserCreate, UserLogin, TokenResponse, UserResponse, RoleResponse
from auth import create_access_token, verify_password, get_password_hash
from migrations import run_migrations, get_database_info

load_dotenv()

app = FastAPI(title="Vehicle Tracking API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ejecutar migraciones automáticamente al iniciar
print("🔄 Ejecutando migraciones de BD...")
run_migrations()
print("✅ Migraciones completadas")

# Authentication endpoints
@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
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
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        phone=user.phone,
        role_id=role_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Obtener el nombre del rol
    role_name = db.query(Role).filter(Role.id == role_id).first().name
    
    return {
        "message": "User created successfully",
        "role": role_name,
        "is_first_user": user_count == 0
    }

@app.post("/login")
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_credentials.email).first()
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Actualizar last_login
    user.last_login = datetime.utcnow()
    db.commit()
    
    access_token = create_access_token(data={"sub": user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 1800,
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "phone": user.phone,
            "role": user.role.name if user.role else None,
            "is_active": user.is_active
        }
    }

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@app.get("/roles")
def get_roles(db: Session = Depends(get_db)):
    roles = db.query(Role).all()
    return roles

@app.get("/health")
def health_check():
    """Endpoint para verificar el estado de la aplicación y BD"""
    db_info = get_database_info()
    return {
        "status": "healthy",
        "database": db_info,
        "message": "API funcionando correctamente"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)