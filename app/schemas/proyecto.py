from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class EstadoProyectoEnum(str, Enum):
    """Estados posibles de un proyecto."""
    PLANIFICACION = "planificacion"
    EN_PROGRESO = "en_progreso"
    PAUSADO = "pausado"
    COMPLETADO = "completado"
    CANCELADO = "cancelado"


class ProyectoBase(BaseModel):
    """Esquema base para proyecto."""
    nombre: str = Field(..., min_length=1, max_length=200)
    descripcion: Optional[str] = None
    cliente_id: int = Field(..., gt=0)
    estado: EstadoProyectoEnum = EstadoProyectoEnum.PLANIFICACION
    fecha_inicio: Optional[datetime] = None
    fecha_fin_estimada: Optional[datetime] = None
    fecha_fin_real: Optional[datetime] = None
    presupuesto: float = Field(..., ge=0)
    costo_real: float = Field(default=0.0, ge=0)
    horas_estimadas: float = Field(default=0.0, ge=0)
    horas_trabajadas: float = Field(default=0.0, ge=0)
    progreso: float = Field(default=0.0, ge=0, le=100)
    prioridad: int = Field(default=1, ge=1, le=3)
    notas: Optional[str] = None
    activo: bool = True

    @validator('fecha_fin_estimada')
    def fecha_fin_debe_ser_posterior_a_inicio(cls, v, values):
        if v and values.get('fecha_inicio') and v <= values.get('fecha_inicio'):
            raise ValueError('La fecha fin estimada debe ser posterior a la fecha de inicio')
        return v

    @validator('presupuesto')
    def presupuesto_positivo(cls, v):
        if v < 0:
            raise ValueError('El presupuesto debe ser positivo')
        return v


class ProyectoCreate(ProyectoBase):
    """Esquema para crear proyecto."""
    colaboradores_ids: Optional[List[int]] = []


class ProyectoUpdate(BaseModel):
    """Esquema para actualizar proyecto."""
    nombre: Optional[str] = Field(None, min_length=1, max_length=200)
    descripcion: Optional[str] = None
    cliente_id: Optional[int] = Field(None, gt=0)
    estado: Optional[EstadoProyectoEnum] = None
    fecha_inicio: Optional[datetime] = None
    fecha_fin_estimada: Optional[datetime] = None
    fecha_fin_real: Optional[datetime] = None
    presupuesto: Optional[float] = Field(None, ge=0)
    costo_real: Optional[float] = Field(None, ge=0)
    horas_estimadas: Optional[float] = Field(None, ge=0)
    horas_trabajadas: Optional[float] = Field(None, ge=0)
    progreso: Optional[float] = Field(None, ge=0, le=100)
    prioridad: Optional[int] = Field(None, ge=1, le=3)
    notas: Optional[str] = None
    activo: Optional[bool] = None
    colaboradores_ids: Optional[List[int]] = None


class ProyectoResponse(ProyectoBase):
    """Esquema de respuesta para proyecto."""
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    
    # Información del cliente
    cliente: Optional[dict] = None
    
    # Información de colaboradores
    colaboradores: Optional[List[dict]] = None
    
    # Estadísticas calculadas
    dias_restantes: Optional[int] = None
    porcentaje_presupuesto_usado: Optional[float] = None
    eficiencia_horas: Optional[float] = None
    
    class Config:
        from_attributes = True


class ProyectoList(BaseModel):
    """Esquema para lista de proyectos."""
    proyectos: List[ProyectoResponse]
    total: int
    pagina: int
    tamaño_pagina: int
    total_paginas: int


class AsignarColaborador(BaseModel):
    """Esquema para asignar colaborador a proyecto."""
    colaborador_id: int = Field(..., gt=0)
    horas_asignadas: float = Field(default=0.0, ge=0)


class EstadisticasProyecto(BaseModel):
    """Esquema para estadísticas de proyectos."""
    total_proyectos: int
    proyectos_activos: int
    proyectos_completados: int
    proyectos_en_progreso: int
    presupuesto_total: float
    costo_total: float
    promedio_progreso: float
    proyectos_por_estado: dict
    proyectos_por_cliente: dict


class ProyectoResumen(BaseModel):
    """Esquema para resumen de proyecto."""
    id: int
    nombre: str
    cliente: str
    estado: EstadoProyectoEnum
    progreso: float
    presupuesto: float
    costo_real: float
    fecha_inicio: Optional[datetime]
    fecha_fin_estimada: Optional[datetime]
    
    class Config:
        from_attributes = True
