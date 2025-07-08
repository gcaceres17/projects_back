from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime


class UsuarioBase(BaseModel):
    """Esquema base para usuario."""
    email: EmailStr
    nombre: str = Field(..., min_length=1, max_length=100)
    apellido: str = Field(..., min_length=1, max_length=100)
    es_admin: bool = False
    activo: bool = True


class UsuarioCreate(UsuarioBase):
    """Esquema para crear usuario."""
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not any(c.isupper() for c in v):
            raise ValueError('La contraseña debe tener al menos una mayúscula')
        if not any(c.islower() for c in v):
            raise ValueError('La contraseña debe tener al menos una minúscula')
        if not any(c.isdigit() for c in v):
            raise ValueError('La contraseña debe tener al menos un número')
        return v


class UsuarioUpdate(BaseModel):
    """Esquema para actualizar usuario."""
    email: Optional[EmailStr] = None
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    apellido: Optional[str] = Field(None, min_length=1, max_length=100)
    es_admin: Optional[bool] = None
    activo: Optional[bool] = None


class UsuarioResponse(UsuarioBase):
    """Esquema de respuesta para usuario."""
    id: int
    fecha_ultimo_acceso: Optional[datetime]
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    
    class Config:
        from_attributes = True


class UsuarioLogin(BaseModel):
    """Esquema para login de usuario."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Esquema para token de acceso."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Esquema para datos del token."""
    email: Optional[str] = None


class CambiarPassword(BaseModel):
    """Esquema para cambiar contraseña."""
    password_actual: str
    password_nueva: str = Field(..., min_length=8)
    
    @validator('password_nueva')
    def validate_password_nueva(cls, v):
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not any(c.isupper() for c in v):
            raise ValueError('La contraseña debe tener al menos una mayúscula')
        if not any(c.islower() for c in v):
            raise ValueError('La contraseña debe tener al menos una minúscula')
        if not any(c.isdigit() for c in v):
            raise ValueError('La contraseña debe tener al menos un número')
        return v
