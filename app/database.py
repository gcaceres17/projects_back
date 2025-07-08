from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.config import settings
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear el motor de la base de datos
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=10,
    max_overflow=20,
    echo=settings.DEBUG,  # Logs SQL queries en desarrollo
)

# Crear una sesión de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear la clase base para los modelos
Base = declarative_base()


def get_db():
    """
    Generador de dependencia para obtener una sesión de base de datos.
    
    Yields:
        Session: Sesión de SQLAlchemy
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Error en la sesión de base de datos: {e}")
        db.rollback()
        raise
    finally:
        db.close()


async def create_tables():
    """
    Crear todas las tablas en la base de datos.
    
    Esta función debe ser llamada al iniciar la aplicación.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Tablas creadas exitosamente")
    except Exception as e:
        logger.error(f"Error al crear tablas: {e}")
        raise


async def drop_tables():
    """
    Eliminar todas las tablas de la base de datos.
    
    ¡Usar con precaución! Solo para desarrollo.
    """
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Tablas eliminadas exitosamente")
    except Exception as e:
        logger.error(f"Error al eliminar tablas: {e}")
        raise
