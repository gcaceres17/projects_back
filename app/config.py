from pydantic_settings import BaseSettings
from typing import List, Optional
from pydantic import validator
import os


class Settings(BaseSettings):
    """
    Configuración de la aplicación usando Pydantic Settings.
    
    Obtiene las variables de entorno y proporciona valores por defecto.
    """
    
    # Database
    DATABASE_URL: str
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "proyecto_db"
    DATABASE_USER: str = "usuario"
    DATABASE_PASSWORD: str = "password"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Sistema de Gestión de Proyectos"
    PROJECT_VERSION: str = "1.0.0"
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Convierte string de URLs separadas por comas a lista."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Email Configuration
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_ENABLED: bool = False
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # Redis Configuration (opcional)
    REDIS_URL: Optional[str] = None
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Timezone
    TIMEZONE: str = "America/Bogota"
    
    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> str:
        """Construye la URL de la base de datos si no está definida."""
        if isinstance(v, str):
            return v
        return f"postgresql://{values.get('DATABASE_USER')}:{values.get('DATABASE_PASSWORD')}@{values.get('DATABASE_HOST')}:{values.get('DATABASE_PORT')}/{values.get('DATABASE_NAME')}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Permitir variables extra del .env


# Instancia global de configuración
settings = Settings()
