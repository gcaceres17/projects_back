from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import logging
import sys

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Imports de la aplicación
from app.config import settings
from app.database import create_tables, get_db
from app.auth import create_first_admin_user
from app.routers import auth, colaboradores, proyectos, clientes, cotizaciones, costos_rigidos, reportes


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestor de ciclo de vida de la aplicación.
    
    Se ejecuta al iniciar y cerrar la aplicación.
    """
    # Startup
    logger.info("Iniciando aplicación...")
    
    try:
        # Crear tablas de base de datos
        await create_tables()
        logger.info("Tablas de base de datos creadas/verificadas")
        
        # Crear usuario administrador por defecto
        from app.database import SessionLocal
        db = SessionLocal()
        try:
            create_first_admin_user(db)
            logger.info("Usuario administrador verificado/creado")
        except Exception as e:
            logger.error(f"Error al crear usuario administrador: {e}")
        finally:
            db.close()
        
        logger.info("Aplicación iniciada exitosamente")
        
    except Exception as e:
        logger.error(f"Error al iniciar aplicación: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Cerrando aplicación...")


# Crear instancia de FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="API REST para Sistema de Gestión de Proyectos",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Manejador de errores global
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Manejador global de excepciones.
    
    Captura y registra todas las excepciones no controladas.
    """
    logger.error(f"Error no controlado: {exc}", exc_info=True)
    
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"}
    )


# Endpoint de salud
@app.get("/health")
async def health_check():
    """
    Endpoint de verificación de salud de la API.
    
    Returns:
        dict: Estado de la aplicación
    """
    return {
        "status": "healthy",
        "version": settings.PROJECT_VERSION,
        "environment": settings.ENVIRONMENT
    }


# Endpoint de información de la API
@app.get("/")
async def root():
    """
    Endpoint raíz con información de la API.
    
    Returns:
        dict: Información básica de la API
    """
    return {
        "message": "Sistema de Gestión de Proyectos API",
        "version": settings.PROJECT_VERSION,
        "docs_url": f"{settings.API_V1_STR}/docs",
        "redoc_url": f"{settings.API_V1_STR}/redoc"
    }


# Endpoint de información de la base de datos
@app.get(f"{settings.API_V1_STR}/database/status")
async def database_status(db: Session = Depends(get_db)):
    """
    Verificar estado de la base de datos.
    
    Args:
        db: Sesión de base de datos
        
    Returns:
        dict: Estado de la conexión a la base de datos
    """
    try:
        # Ejecutar una consulta simple para verificar la conexión
        db.execute("SELECT 1")
        return {
            "status": "connected",
            "database": "postgresql",
            "message": "Conexión a base de datos exitosa"
        }
    except Exception as e:
        logger.error(f"Error de conexión a base de datos: {e}")
        return {
            "status": "error",
            "database": "postgresql",
            "message": f"Error de conexión: {str(e)}"
        }


# Incluir routers
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["Autenticación"]
)

app.include_router(
    colaboradores.router,
    prefix=f"{settings.API_V1_STR}/colaboradores",
    tags=["Colaboradores"]
)

app.include_router(
    proyectos.router,
    prefix=f"{settings.API_V1_STR}/proyectos",
    tags=["Proyectos"]
)

app.include_router(
    clientes.router,
    prefix=f"{settings.API_V1_STR}/clientes",
    tags=["Clientes"]
)

app.include_router(
    cotizaciones.router,
    prefix=f"{settings.API_V1_STR}/cotizaciones",
    tags=["Cotizaciones"]
)

app.include_router(
    costos_rigidos.router,
    prefix=f"{settings.API_V1_STR}/costos-rigidos",
    tags=["Costos Rígidos"]
)

app.include_router(
    reportes.router,
    prefix=f"{settings.API_V1_STR}/reportes",
    tags=["Reportes"]
)


# Middleware para logging de requests
@app.middleware("http")
async def log_requests(request, call_next):
    """
    Middleware para registrar todas las peticiones HTTP.
    
    Args:
        request: Petición HTTP
        call_next: Siguiente función en la cadena
        
    Returns:
        Response: Respuesta HTTP
    """
    import time
    
    start_time = time.time()
    
    # Procesar petición
    response = await call_next(request)
    
    # Calcular tiempo de procesamiento
    process_time = time.time() - start_time
    
    # Registrar petición
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.4f}s"
    )
    
    return response


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
