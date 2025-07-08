from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class TipoColaboradorEnum(str, Enum):
    """Tipos de colaborador."""
    INTERNO = "interno"
    EXTERNO = "externo"
    FREELANCE = "freelance"


class ColaboradorBase(BaseModel):
    """Esquema base para colaborador."""
    nombre: str = Field(..., min_length=1, max_length=100)
    apellido: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    telefono: Optional[str] = Field(None, max_length=20)
    cargo: str = Field(..., min_length=1, max_length=100)
    departamento: Optional[str] = Field(None, max_length=100)
    tipo: TipoColaboradorEnum = TipoColaboradorEnum.INTERNO
    costo_hora: float = Field(..., ge=0)
    disponible: bool = True
    habilidades: Optional[str] = None
    fecha_ingreso: Optional[datetime] = None
    activo: bool = True


class ColaboradorCreate(ColaboradorBase):
    """Esquema para crear colaborador."""
    pass


class ColaboradorUpdate(BaseModel):
    """Esquema para actualizar colaborador."""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    apellido: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    telefono: Optional[str] = Field(None, max_length=20)
    cargo: Optional[str] = Field(None, min_length=1, max_length=100)
    departamento: Optional[str] = Field(None, max_length=100)
    tipo: Optional[TipoColaboradorEnum] = None
    costo_hora: Optional[float] = Field(None, ge=0)
    disponible: Optional[bool] = None
    habilidades: Optional[str] = None
    fecha_ingreso: Optional[datetime] = None
    activo: Optional[bool] = None


class ColaboradorResponse(ColaboradorBase):
    """Esquema de respuesta para colaborador."""
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    
    class Config:
        from_attributes = True


class ColaboradorList(BaseModel):
    """Esquema para lista de colaboradores."""
    colaboradores: List[ColaboradorResponse]
    total: int
    pagina: int
    tamaño_pagina: int
    total_paginas: int


# Esquemas para estadísticas de colaboradores
class EstadisticasColaborador(BaseModel):
    """Esquema para estadísticas de colaboradores."""
    total_colaboradores: int
    colaboradores_activos: int
    colaboradores_disponibles: int
    promedio_costo_hora: float
    total_por_tipo: dict
    total_por_departamento: dict
