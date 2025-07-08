from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class EstadoCotizacionEnum(str, Enum):
    """Estados posibles de una cotización."""
    BORRADOR = "borrador"
    ENVIADA = "enviada"
    APROBADA = "aprobada"
    RECHAZADA = "rechazada"
    VENCIDA = "vencida"


class ItemCotizacionBase(BaseModel):
    """Esquema base para item de cotización."""
    descripcion: str = Field(..., min_length=1, max_length=500)
    cantidad: float = Field(..., gt=0)
    precio_unitario: float = Field(..., ge=0)
    orden: int = Field(default=1, ge=1)
    activo: bool = True


class ItemCotizacionCreate(ItemCotizacionBase):
    """Esquema para crear item de cotización."""
    pass


class ItemCotizacionUpdate(BaseModel):
    """Esquema para actualizar item de cotización."""
    descripcion: Optional[str] = Field(None, min_length=1, max_length=500)
    cantidad: Optional[float] = Field(None, gt=0)
    precio_unitario: Optional[float] = Field(None, ge=0)
    orden: Optional[int] = Field(None, ge=1)
    activo: Optional[bool] = None


class ItemCotizacionResponse(ItemCotizacionBase):
    """Esquema de respuesta para item de cotización."""
    id: int
    cotizacion_id: int
    subtotal: float
    
    class Config:
        from_attributes = True


class CotizacionBase(BaseModel):
    """Esquema base para cotización."""
    cliente_id: int = Field(..., gt=0)
    proyecto_id: Optional[int] = Field(None, gt=0)
    titulo: str = Field(..., min_length=1, max_length=200)
    descripcion: Optional[str] = None
    descuento: float = Field(default=0.0, ge=0)
    estado: EstadoCotizacionEnum = EstadoCotizacionEnum.BORRADOR
    fecha_vencimiento: Optional[datetime] = None
    validez_dias: int = Field(default=30, ge=1)
    terminos_condiciones: Optional[str] = None
    notas: Optional[str] = None
    activo: bool = True

    @validator('fecha_vencimiento')
    def fecha_vencimiento_futura(cls, v):
        if v and v <= datetime.now():
            raise ValueError('La fecha de vencimiento debe ser futura')
        return v

    @validator('descuento')
    def descuento_valido(cls, v):
        if v < 0 or v > 100:
            raise ValueError('El descuento debe estar entre 0 y 100')
        return v


class CotizacionCreate(CotizacionBase):
    """Esquema para crear cotización."""
    items: List[ItemCotizacionCreate] = []


class CotizacionUpdate(BaseModel):
    """Esquema para actualizar cotización."""
    cliente_id: Optional[int] = Field(None, gt=0)
    proyecto_id: Optional[int] = Field(None, gt=0)
    titulo: Optional[str] = Field(None, min_length=1, max_length=200)
    descripcion: Optional[str] = None
    descuento: Optional[float] = Field(None, ge=0, le=100)
    estado: Optional[EstadoCotizacionEnum] = None
    fecha_vencimiento: Optional[datetime] = None
    validez_dias: Optional[int] = Field(None, ge=1)
    terminos_condiciones: Optional[str] = None
    notas: Optional[str] = None
    activo: Optional[bool] = None
    items: Optional[List[ItemCotizacionUpdate]] = None


class CotizacionResponse(CotizacionBase):
    """Esquema de respuesta para cotización."""
    id: int
    numero: str
    subtotal: float
    impuestos: float
    total: float
    fecha_creacion: datetime
    fecha_envio: Optional[datetime]
    fecha_aprobacion: Optional[datetime]
    
    # Información del cliente
    cliente: Optional[dict] = None
    
    # Información del proyecto
    proyecto: Optional[dict] = None
    
    # Items de la cotización
    items: Optional[List[ItemCotizacionResponse]] = None
    
    # Campos calculados
    dias_para_vencimiento: Optional[int] = None
    porcentaje_impuestos: Optional[float] = None
    
    class Config:
        from_attributes = True


class CotizacionList(BaseModel):
    """Esquema para lista de cotizaciones."""
    cotizaciones: List[CotizacionResponse]
    total: int
    pagina: int
    tamaño_pagina: int
    total_paginas: int


class CotizacionResumen(BaseModel):
    """Esquema para resumen de cotización."""
    id: int
    numero: str
    titulo: str
    cliente: str
    estado: EstadoCotizacionEnum
    total: float
    fecha_creacion: datetime
    fecha_vencimiento: Optional[datetime]
    
    class Config:
        from_attributes = True


class EstadisticasCotizacion(BaseModel):
    """Esquema para estadísticas de cotizaciones."""
    total_cotizaciones: int
    cotizaciones_por_estado: dict
    valor_total_cotizaciones: float
    valor_cotizaciones_aprobadas: float
    tasa_aprobacion: float
    promedio_valor_cotizacion: float
    cotizaciones_vencidas: int
    cotizaciones_por_mes: dict


class EnviarCotizacion(BaseModel):
    """Esquema para enviar cotización."""
    email_destinatario: str
    asunto: Optional[str] = None
    mensaje: Optional[str] = None
    incluir_pdf: bool = True
