from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class TipoCostoEnum(str, Enum):
    """Tipos de costo rígido."""
    FIJO = "fijo"
    VARIABLE = "variable"
    RECURRENTE = "recurrente"


class CostoRigidoBase(BaseModel):
    """Esquema base para costo rígido."""
    proyecto_id: Optional[int] = Field(None, gt=0)
    nombre: str = Field(..., min_length=1, max_length=200)
    descripcion: Optional[str] = None
    tipo: TipoCostoEnum = TipoCostoEnum.FIJO
    valor: float = Field(..., gt=0)
    moneda: str = Field(default="USD", max_length=10)
    frecuencia: Optional[str] = Field(None, max_length=50)
    fecha_aplicacion: Optional[datetime] = None
    categoria: Optional[str] = Field(None, max_length=100)
    proveedor: Optional[str] = Field(None, max_length=200)
    activo: bool = True

    @validator('valor')
    def valor_positivo(cls, v):
        if v <= 0:
            raise ValueError('El valor debe ser positivo')
        return v

    @validator('moneda')
    def moneda_valida(cls, v):
        monedas_validas = ['USD', 'EUR', 'COP', 'MXN', 'ARS', 'PEN', 'CLP']
        if v not in monedas_validas:
            raise ValueError(f'Moneda debe ser una de: {", ".join(monedas_validas)}')
        return v


class CostoRigidoCreate(CostoRigidoBase):
    """Esquema para crear costo rígido."""
    pass


class CostoRigidoUpdate(BaseModel):
    """Esquema para actualizar costo rígido."""
    proyecto_id: Optional[int] = Field(None, gt=0)
    nombre: Optional[str] = Field(None, min_length=1, max_length=200)
    descripcion: Optional[str] = None
    tipo: Optional[TipoCostoEnum] = None
    valor: Optional[float] = Field(None, gt=0)
    moneda: Optional[str] = Field(None, max_length=10)
    frecuencia: Optional[str] = Field(None, max_length=50)
    fecha_aplicacion: Optional[datetime] = None
    categoria: Optional[str] = Field(None, max_length=100)
    proveedor: Optional[str] = Field(None, max_length=200)
    activo: Optional[bool] = None


class CostoRigidoResponse(CostoRigidoBase):
    """Esquema de respuesta para costo rígido."""
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    
    # Información del proyecto
    proyecto: Optional[dict] = None
    
    # Campos calculados
    valor_anual: Optional[float] = None
    valor_mensual: Optional[float] = None
    
    class Config:
        from_attributes = True


class CostoRigidoList(BaseModel):
    """Esquema para lista de costos rígidos."""
    costos: List[CostoRigidoResponse]
    total: int
    pagina: int
    tamaño_pagina: int
    total_paginas: int


class CostoRigidoResumen(BaseModel):
    """Esquema para resumen de costo rígido."""
    id: int
    nombre: str
    tipo: TipoCostoEnum
    valor: float
    moneda: str
    categoria: Optional[str]
    proyecto: Optional[str]
    
    class Config:
        from_attributes = True


class EstadisticasCostoRigido(BaseModel):
    """Esquema para estadísticas de costos rígidos."""
    total_costos: int
    costos_por_tipo: dict
    costos_por_categoria: dict
    valor_total_costos: float
    valor_costos_fijos: float
    valor_costos_variables: float
    valor_costos_recurrentes: float
    costos_por_proyecto: dict
    costos_por_moneda: dict


class CostosPorCategoria(BaseModel):
    """Esquema para costos agrupados por categoría."""
    categoria: str
    total_costos: int
    valor_total: float
    costos: List[CostoRigidoResumen]


class CostosPorProyecto(BaseModel):
    """Esquema para costos agrupados por proyecto."""
    proyecto_id: int
    proyecto_nombre: str
    total_costos: int
    valor_total: float
    costos: List[CostoRigidoResumen]
