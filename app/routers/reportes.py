"""
Router para endpoints de reportes.

Este módulo maneja todas las operaciones relacionadas con reportes del sistema.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, text
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from app.database import get_db
from app.auth import get_current_user
from app.models import Usuario, Proyecto, Colaborador, Cotizacion, CostoRigido, Cliente, EstadoProyecto, EstadoCotizacion
# from app.services.pdf_service import PDFGenerator  # TODO: Implementar servicio PDF

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener estadísticas generales del dashboard.
    
    Args:
        db: Sesión de base de datos
        current_user: Usuario actual autenticado
        
    Returns:
        dict: Estadísticas del dashboard
    """
    try:
        # Estadísticas de proyectos
        total_proyectos = db.query(Proyecto).count()
        proyectos_activos = db.query(Proyecto).filter(
            Proyecto.estado == EstadoProyecto.EN_PROGRESO
        ).count()
        proyectos_completados = db.query(Proyecto).filter(
            Proyecto.estado == EstadoProyecto.COMPLETADO
        ).count()
        
        # Estadísticas de colaboradores
        total_colaboradores = db.query(Colaborador).count()
        colaboradores_activos = db.query(Colaborador).filter(
            Colaborador.activo == True
        ).count()
        
        # Estadísticas de cotizaciones
        total_cotizaciones = db.query(Cotizacion).count()
        cotizaciones_pendientes = db.query(Cotizacion).filter(
            Cotizacion.estado == EstadoCotizacion.ENVIADA
        ).count()
        cotizaciones_aprobadas = db.query(Cotizacion).filter(
            Cotizacion.estado == EstadoCotizacion.APROBADA
        ).count()
        
        # Estadísticas de clientes
        total_clientes = db.query(Cliente).count()
        clientes_activos = db.query(Cliente).filter(
            Cliente.activo == True
        ).count()
        
        # Valor total de cotizaciones
        valor_total_cotizaciones = db.query(
            func.sum(Cotizacion.total)
        ).scalar() or 0
        
        valor_cotizaciones_aprobadas = db.query(
            func.sum(Cotizacion.total)
        ).filter(
            Cotizacion.estado == EstadoCotizacion.APROBADA
        ).scalar() or 0
        
        return {
            "proyectos": {
                "total": total_proyectos,
                "activos": proyectos_activos,
                "completados": proyectos_completados,
                "porcentaje_completados": (
                    (proyectos_completados / total_proyectos * 100) 
                    if total_proyectos > 0 else 0
                )
            },
            "colaboradores": {
                "total": total_colaboradores,
                "activos": colaboradores_activos,
                "porcentaje_activos": (
                    (colaboradores_activos / total_colaboradores * 100) 
                    if total_colaboradores > 0 else 0
                )
            },
            "cotizaciones": {
                "total": total_cotizaciones,
                "pendientes": cotizaciones_pendientes,
                "aprobadas": cotizaciones_aprobadas,
                "valor_total": float(valor_total_cotizaciones),
                "valor_aprobadas": float(valor_cotizaciones_aprobadas)
            },
            "clientes": {
                "total": total_clientes,
                "activos": clientes_activos,
                "porcentaje_activos": (
                    (clientes_activos / total_clientes * 100) 
                    if total_clientes > 0 else 0
                )
            }
        }
    
    except Exception as e:
        logger.error(f"Error al obtener estadísticas del dashboard: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener estadísticas del dashboard"
        )


@router.get("/dashboard-test")
async def get_dashboard_stats_test():
    """
    Endpoint de prueba para dashboard sin autenticación.
    Devuelve datos de ejemplo para testing.
    """
    return {
        "proyectos": {
            "total": 5,
            "activos": 3,
            "completados": 2,
            "porcentaje_completados": 40.0
        },
        "colaboradores": {
            "total": 8,
            "activos": 7,
            "porcentaje_activos": 87.5
        },
        "cotizaciones": {
            "total": 12,
            "pendientes": 4,
            "aprobadas": 6,
            "valor_total": 25000000.0,
            "valor_aprobadas": 15000000.0
        },
        "clientes": {
            "total": 10,
            "activos": 8,
            "porcentaje_activos": 80.0
        }
    }


@router.get("/proyectos-por-estado")
async def get_proyectos_por_estado(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener distribución de proyectos por estado.
    
    Args:
        db: Sesión de base de datos
        current_user: Usuario actual autenticado
        
    Returns:
        List[dict]: Distribución de proyectos por estado
    """
    try:
        resultado = db.query(
            Proyecto.estado,
            func.count(Proyecto.id).label('cantidad')
        ).group_by(Proyecto.estado).all()
        
        return [
            {
                "estado": estado,
                "cantidad": cantidad
            }
            for estado, cantidad in resultado
        ]
    
    except Exception as e:
        logger.error(f"Error al obtener proyectos por estado: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener proyectos por estado"
        )


@router.get("/cotizaciones-por-mes")
async def get_cotizaciones_por_mes(
    año: int = Query(default=datetime.now().year, description="Año para el reporte"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener cotizaciones agrupadas por mes.
    
    Args:
        año: Año para el reporte
        db: Sesión de base de datos
        current_user: Usuario actual autenticado
        
    Returns:
        List[dict]: Cotizaciones por mes
    """
    try:
        resultado = db.query(
            extract('month', Cotizacion.fecha_creacion).label('mes'),
            func.count(Cotizacion.id).label('cantidad'),
            func.sum(Cotizacion.total).label('valor_total')
        ).filter(
            extract('year', Cotizacion.fecha_creacion) == año
        ).group_by(
            extract('month', Cotizacion.fecha_creacion)
        ).order_by(
            extract('month', Cotizacion.fecha_creacion)
        ).all()
        
        meses = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        
        return [
            {
                "mes": meses[int(mes) - 1],
                "numero_mes": int(mes),
                "cantidad": cantidad,
                "valor_total": float(valor_total or 0)
            }
            for mes, cantidad, valor_total in resultado
        ]
    
    except Exception as e:
        logger.error(f"Error al obtener cotizaciones por mes: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener cotizaciones por mes"
        )


@router.get("/costos-rigidos-resumen")
async def get_costos_rigidos_resumen(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener resumen de costos rígidos.
    
    Args:
        db: Sesión de base de datos
        current_user: Usuario actual autenticado
        
    Returns:
        dict: Resumen de costos rígidos
    """
    try:
        # Costos por categoría
        costos_por_categoria = db.query(
            CostoRigido.categoria,
            func.count(CostoRigido.id).label('cantidad'),
            func.sum(CostoRigido.monto).label('total')
        ).group_by(CostoRigido.categoria).all()
        
        # Total de costos rígidos
        total_costos = db.query(
            func.sum(CostoRigido.monto)
        ).scalar() or 0
        
        return {
            "total_costos": float(total_costos),
            "por_categoria": [
                {
                    "categoria": categoria,
                    "cantidad": cantidad,
                    "total": float(total)
                }
                for categoria, cantidad, total in costos_por_categoria
            ]
        }
    
    except Exception as e:
        logger.error(f"Error al obtener resumen de costos rígidos: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener resumen de costos rígidos"
        )


@router.get("/colaboradores-productividad")
async def get_colaboradores_productividad(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener reporte de productividad de colaboradores.
    
    Args:
        db: Sesión de base de datos
        current_user: Usuario actual autenticado
        
    Returns:
        List[dict]: Productividad por colaborador
    """
    try:
        # Obtener colaboradores con conteo de proyectos
        resultado = db.query(
            Colaborador.id,
            Colaborador.nombre,
            Colaborador.email,
            Colaborador.especialidad,
            func.count(Proyecto.id).label('proyectos_asignados')
        ).outerjoin(
            Proyecto, Colaborador.id == Proyecto.claborador_principal_id
        ).group_by(
            Colaborador.id,
            Colaborador.nombre,
            Colaborador.email,
            Colaborador.especialidad
        ).filter(
            Colaborador.activo == True
        ).all()
        
        return [
            {
                "id": colaborador_id,
                "nombre": nombre,
                "email": email,
                "especialidad": especialidad,
                "proyectos_asignados": proyectos_asignados
            }
            for colaborador_id, nombre, email, especialidad, proyectos_asignados in resultado
        ]
    
    except Exception as e:
        logger.error(f"Error al obtener productividad de colaboradores: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener productividad de colaboradores"
        )


@router.get("/clientes-mas-activos")
async def get_clientes_mas_activos(
    limite: int = Query(default=10, description="Número máximo de clientes a retornar"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener clientes más activos (con más proyectos).
    
    Args:
        limite: Número máximo de clientes a retornar
        db: Sesión de base de datos
        current_user: Usuario actual autenticado
        
    Returns:
        List[dict]: Clientes más activos
    """
    try:
        resultado = db.query(
            Cliente.id,
            Cliente.nombre,
            Cliente.email,
            Cliente.telefono,
            func.count(Proyecto.id).label('total_proyectos')
        ).outerjoin(
            Proyecto, Cliente.id == Proyecto.cliente_id
        ).group_by(
            Cliente.id,
            Cliente.nombre,
            Cliente.email,
            Cliente.telefono
        ).filter(
            Cliente.activo == True
        ).order_by(
            func.count(Proyecto.id).desc()
        ).limit(limite).all()
        
        return [
            {
                "id": cliente_id,
                "nombre": nombre,
                "email": email,
                "telefono": telefono,
                "total_proyectos": total_proyectos
            }
            for cliente_id, nombre, email, telefono, total_proyectos in resultado
        ]
    
    except Exception as e:
        logger.error(f"Error al obtener clientes más activos: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener clientes más activos"
        )


@router.get("/resumen-financiero")
async def get_resumen_financiero(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener resumen financiero general.
    
    Args:
        db: Sesión de base de datos
        current_user: Usuario actual autenticado
        
    Returns:
        dict: Resumen financiero
    """
    try:
        # Ingresos de cotizaciones aprobadas
        ingresos_cotizaciones = db.query(
            func.sum(Cotizacion.total)
        ).filter(
            Cotizacion.estado == EstadoCotizacion.APROBADA
        ).scalar() or 0
        
        # Gastos de costos rígidos
        gastos_costos_rigidos = db.query(
            func.sum(CostoRigido.monto)
        ).scalar() or 0
        
        # Margen bruto
        margen_bruto = float(ingresos_cotizaciones) - float(gastos_costos_rigidos)
        
        # Porcentaje de margen
        porcentaje_margen = (
            (margen_bruto / float(ingresos_cotizaciones) * 100) 
            if ingresos_cotizaciones > 0 else 0
        )
        
        return {
            "ingresos_cotizaciones": float(ingresos_cotizaciones),
            "gastos_costos_rigidos": float(gastos_costos_rigidos),
            "margen_bruto": margen_bruto,
            "porcentaje_margen": porcentaje_margen
        }
    
    except Exception as e:
        logger.error(f"Error al obtener resumen financiero: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener resumen financiero"
        )
