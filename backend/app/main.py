from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import engine
from core.migrations import run_migrations, get_database_info
from features.auth.routes import auth_router
from features.users.routes import users_router
from features.roles.routes import roles_router

# Crear aplicación FastAPI
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

# Incluir routers de features
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(roles_router, prefix="/roles", tags=["Roles"])

# Health check endpoint
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
