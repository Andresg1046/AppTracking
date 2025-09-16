from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import engine
from core.migrations import run_migrations, get_database_info
from core.rate_limiting import rate_limit_middleware
from features.auth.routes import auth_router
from features.users.routes import users_router
from features.roles.routes import roles_router
from features.vehicles.routes import vehicles_router
from features.ecommerce.proxy_routes import proxy_router as ecommerce_router
from features.ecommerce.checkout_routes import checkout_router
from features.ecommerce.tax_routes import tax_router
from features.ecommerce.shipping_routes import shipping_router
from features.ecommerce.woocommerce_cart_routes import woocommerce_cart_router
from features.ecommerce.test_woocommerce_routes import test_woocommerce_router
from features.tracking.routes import tracking_router

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

# Rate limiting middleware
app.middleware("http")(rate_limit_middleware)

# Ejecutar migraciones automáticamente al iniciar
print("🔄 Ejecutando migraciones de BD...")
run_migrations()
print("✅ Migraciones completadas")

# Incluir routers de features
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(roles_router, prefix="/roles", tags=["Roles"])
app.include_router(vehicles_router, prefix="/vehicles", tags=["Vehicles"])
app.include_router(ecommerce_router, prefix="/ecommerce", tags=["E-commerce"])
app.include_router(checkout_router, prefix="/checkout", tags=["Checkout"])
app.include_router(tax_router, prefix="/tax", tags=["Tax"])
app.include_router(shipping_router, prefix="/shipping", tags=["Shipping"])
app.include_router(woocommerce_cart_router, prefix="/ecommerce", tags=["WooCommerce Cart"])
app.include_router(test_woocommerce_router, prefix="/test", tags=["Test WooCommerce"])
app.include_router(tracking_router, prefix="/tracking", tags=["Tracking"])

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
