from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.openapi.utils import get_openapi
import logging
from contextlib import asynccontextmanager
from database import engine, Base
from api.routes import auth, productos, categorias, usuarios, ventas, gastos, carrito, reportes, estadisticas
from config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    logger.info("Base de datos inicializada")
    yield

app = FastAPI(
    title="Textcort API",
    description="Backend FastAPI para plataforma e-commerce con Flask",
    version="1.0.0",
    lifespan=lifespan,
    # Configuración de Swagger UI para OAuth2
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": True,
    }
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Autenticación"])
app.include_router(usuarios.router, prefix="/api/usuarios", tags=["Usuarios"])
app.include_router(productos.router, prefix="/api/productos", tags=["Productos"])
app.include_router(categorias.router, prefix="/api/categorias", tags=["Categorías"])
app.include_router(carrito.router, prefix="/api/carrito", tags=["Carrito"])
app.include_router(ventas.router, prefix="/api/ventas", tags=["Ventas"])
app.include_router(gastos.router, prefix="/api/gastos", tags=["Gastos"])
app.include_router(reportes.router, prefix="/api/reportes", tags=["Reportes"])
app.include_router(estadisticas.router, prefix="/api/estadisticas", tags=["Estadísticas"])


# Personalizar OpenAPI schema para seguridad OAuth2
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Agregar esquema de seguridad OAuth2
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "api/auth/login",
                    "scopes": {}
                }
            }
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/")
async def root():
    return {
        "message": "Bienvenido a Textcort API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8033)