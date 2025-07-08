from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class TipoReporte(str, Enum):
    """Tipos de reportes disponibles."""
    PROYECTOS = "proyectos"
    COLABORADORES = "colaboradores"
    COTIZACIONES = "cotizaciones"
    COSTOS = "costos"
    FINANCIERO = "financiero"
    RENDIMIENTO = "rendimiento"


class PeriodoReporte(str, Enum):
    """Períodos para reportes."""
    DIARIO = "diario"
    SEMANAL = "semanal"
    MENSUAL = "mensual"
    TRIMESTRAL = "trimestral"
    ANUAL = "anual"
    PERSONALIZADO = "personalizado"


class FormatoReporte(str, Enum):
    """Formatos de exportación."""
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"


class FiltroReporte(BaseModel):
    """Filtros para generar reportes."""
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    proyecto_ids: Optional[List[int]] = None
    cliente_ids: Optional[List[int]] = None
    colaborador_ids: Optional[List[int]] = None
    estados: Optional[List[str]] = None
    categorias: Optional[List[str]] = None
    incluir_inactivos: bool = False


class ReporteRequest(BaseModel):
    """Esquema para solicitud de reporte."""
    tipo: TipoReporte
    periodo: PeriodoReporte = PeriodoReporte.MENSUAL
    formato: FormatoReporte = FormatoReporte.PDF
    filtros: Optional[FiltroReporte] = None
    incluir_graficos: bool = True
    incluir_detalles: bool = True
    titulo_personalizado: Optional[str] = None


class ResumenFinanciero(BaseModel):
    """Esquema para resumen financiero."""
    ingresos_totales: float
    gastos_totales: float
    utilidad_bruta: float
    margen_utilidad: float
    proyectos_rentables: int
    proyectos_no_rentables: int
    ingresos_por_mes: Dict[str, float]
    gastos_por_mes: Dict[str, float]


class RendimientoProyecto(BaseModel):
    """Esquema para rendimiento de proyectos."""
    proyecto_id: int
    nombre: str
    presupuesto: float
    costo_real: float
    variacion_presupuesto: float
    horas_estimadas: float
    horas_trabajadas: float
    eficiencia_horas: float
    progreso: float
    dias_retraso: int
    rentabilidad: float


class RendimientoColaborador(BaseModel):
    """Esquema para rendimiento de colaboradores."""
    colaborador_id: int
    nombre: str
    horas_trabajadas: float
    proyectos_asignados: int
    proyectos_completados: int
    costo_total: float
    eficiencia: float
    disponibilidad: float


class EstadisticasGenerales(BaseModel):
    """Esquema para estadísticas generales."""
    total_proyectos: int
    proyectos_activos: int
    proyectos_completados: int
    total_colaboradores: int
    colaboradores_activos: int
    total_clientes: int
    clientes_activos: int
    total_cotizaciones: int
    cotizaciones_aprobadas: int
    valor_total_proyectos: float
    valor_total_cotizaciones: float
    promedio_rentabilidad: float


class ReporteResponse(BaseModel):
    """Esquema de respuesta para reporte."""
    id: str
    tipo: TipoReporte
    titulo: str
    periodo: PeriodoReporte
    formato: FormatoReporte
    fecha_generacion: datetime
    filtros_aplicados: Optional[FiltroReporte]
    
    # Datos del reporte
    resumen_financiero: Optional[ResumenFinanciero] = None
    rendimiento_proyectos: Optional[List[RendimientoProyecto]] = None
    rendimiento_colaboradores: Optional[List[RendimientoColaborador]] = None
    estadisticas_generales: Optional[EstadisticasGenerales] = None
    
    # Información del archivo
    archivo_url: Optional[str] = None
    tamaño_archivo: Optional[int] = None
    
    class Config:
        from_attributes = True


class DashboardData(BaseModel):
    """Esquema para datos del dashboard."""
    estadisticas_generales: EstadisticasGenerales
    proyectos_recientes: List[Dict[str, Any]]
    cotizaciones_pendientes: List[Dict[str, Any]]
    colaboradores_disponibles: List[Dict[str, Any]]
    alertas: List[Dict[str, Any]]
    graficos: Dict[str, Any]


class Alerta(BaseModel):
    """Esquema para alertas del sistema."""
    tipo: str
    mensaje: str
    nivel: str  # info, warning, error
    fecha: datetime
    leida: bool = False
    proyecto_id: Optional[int] = None
    cotizacion_id: Optional[int] = None
