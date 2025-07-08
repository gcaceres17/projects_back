from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class ClienteBase(BaseModel):
    """Esquema base para cliente."""
    nombre: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    telefono: Optional[str] = Field(None, max_length=20)
    direccion: Optional[str] = None
    ciudad: Optional[str] = Field(None, max_length=100)
    pais: Optional[str] = Field(None, max_length=100)
    contacto_principal: Optional[str] = Field(None, max_length=200)
    nit_ruc: Optional[str] = Field(None, max_length=50)
    activo: bool = True


class ClienteCreate(ClienteBase):
    """Esquema para crear cliente."""
    pass


class ClienteUpdate(BaseModel):
    """Esquema para actualizar cliente."""
    nombre: Optional[str] = Field(None, min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    telefono: Optional[str] = Field(None, max_length=20)
    direccion: Optional[str] = None
    ciudad: Optional[str] = Field(None, max_length=100)
    pais: Optional[str] = Field(None, max_length=100)
    contacto_principal: Optional[str] = Field(None, max_length=200)
    nit_ruc: Optional[str] = Field(None, max_length=50)
    activo: Optional[bool] = None


class ClienteResponse(ClienteBase):
    """Esquema de respuesta para cliente."""
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    
    # Estadísticas del cliente
    total_proyectos: Optional[int] = None
    proyectos_activos: Optional[int] = None
    total_cotizaciones: Optional[int] = None
    valor_total_proyectos: Optional[float] = None
    
    class Config:
        from_attributes = True


class ClienteList(BaseModel):
    """Esquema para lista de clientes."""
    clientes: List[ClienteResponse]
    total: int
    pagina: int
    tamaño_pagina: int
    total_paginas: int


class ClienteResumen(BaseModel):
    """Esquema para resumen de cliente."""
    id: int
    nombre: str
    email: str
    total_proyectos: int
    proyectos_activos: int
    valor_total: float
    
    class Config:
        from_attributes = True
