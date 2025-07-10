"""
Router para gestión de costos rígidos
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, extract
from datetime import datetime, date

from app.database import get_db
from app.auth import get_current_user
from app.models import CostoRigido, Usuario, Proyecto
from app.schemas import CostoRigidoCreate, CostoRigidoUpdate, CostoRigidoResponse, PaginatedResponse
from app.services.costo_rigido_service import costo_rigido_service

router = APIRouter(prefix="/costos-rigidos", tags=["costos-rigidos"])

# El servicio se importa directamente desde costo_rigido_service


@router.get("", response_model=PaginatedResponse[CostoRigidoResponse])
async def listar_costos_rigidos(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(10, ge=1, le=100, description="Número de registros a devolver"),
    categoria: Optional[str] = Query(None, description="Filtrar por categoría"),
    tipo: Optional[str] = Query(None, description="Filtrar por tipo"),
    proyecto_id: Optional[int] = Query(None, description="Filtrar por proyecto"),
    proveedor: Optional[str] = Query(None, description="Filtrar por proveedor"),
    frecuencia: Optional[str] = Query(None, description="Filtrar por frecuencia"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Listar costos rígidos con paginación y filtros.
    """
    try:
        # Construir filtros
        filters = []
        
        if categoria:
            filters.append(CostoRigido.categoria.ilike(f"%{categoria}%"))
        
        if tipo:
            filters.append(CostoRigido.tipo == tipo)
        
        if proyecto_id:
            filters.append(CostoRigido.proyecto_id == proyecto_id)
        
        if proveedor:
            filters.append(CostoRigido.proveedor.ilike(f"%{proveedor}%"))
        
        if frecuencia:
            filters.append(CostoRigido.frecuencia == frecuencia)
            
        if activo is not None:
            filters.append(CostoRigido.activo == activo)
        
        # Obtener datos paginados
        result = costo_rigido_service.get_paginated(
            db=db,
            skip=skip,
            limit=limit,
            filters=filters,
            order_by=[CostoRigido.fecha_aplicacion.desc()]
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener costos: {str(e)}")


@router.post("", response_model=CostoRigidoResponse, status_code=201)
async def crear_costo_rigido(
    costo_data: CostoRigidoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Crear un nuevo costo rígido.
    """
    try:
        # Verificar que el proyecto existe (si se especifica)
        if costo_data.proyecto_id:
            proyecto = db.query(Proyecto).filter(Proyecto.id == costo_data.proyecto_id).first()
            if not proyecto:
                raise HTTPException(status_code=404, detail="Proyecto no encontrado")
        
        # El costo está listo para crear (sin validación de fecha_fin porque no existe)
        
        # Crear costo
        costo = costo_rigido_service.create(db=db, obj_data=costo_data.dict())
        
        return costo
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear costo: {str(e)}")


@router.get("/{costo_id}", response_model=CostoRigidoResponse)
async def obtener_costo_rigido(
    costo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener costo rígido por ID.
    """
    try:
        costo = costo_rigido_service.get_by_id(db=db, obj_id=costo_id)
        if not costo:
            raise HTTPException(status_code=404, detail="Costo no encontrado")
        
        return costo
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener costo: {str(e)}")


@router.put("/{costo_id}", response_model=CostoRigidoResponse)
async def actualizar_costo_rigido(
    costo_id: int,
    costo_data: CostoRigidoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Actualizar costo rígido existente.
    """
    try:
        # Verificar que el costo existe
        costo_existente = costo_rigido_service.get_by_id(db=db, obj_id=costo_id)
        if not costo_existente:
            raise HTTPException(status_code=404, detail="Costo no encontrado")
        
        # Verificar proyecto si se está actualizando
        if costo_data.proyecto_id:
            proyecto = db.query(Proyecto).filter(Proyecto.id == costo_data.proyecto_id).first()
            if not proyecto:
                raise HTTPException(status_code=404, detail="Proyecto no encontrado")
        
        # Validar fechas si se están actualizando
        update_dict = costo_data.dict(exclude_unset=True)
        fecha_aplicacion = update_dict.get('fecha_aplicacion', costo_existente.fecha_aplicacion)
        # Actualizar costo (sin validación de fecha_fin porque no existe)
        costo = costo_rigido_service.update(
            db=db, 
            obj_id=costo_id, 
            obj_data=update_dict
        )
        
        return costo
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar costo: {str(e)}")


@router.delete("/{costo_id}")
async def eliminar_costo_rigido(
    costo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Eliminar costo rígido (soft delete).
    """
    try:
        # Verificar que el costo existe
        costo = costo_rigido_service.get_by_id(db=db, obj_id=costo_id)
        if not costo:
            raise HTTPException(status_code=404, detail="Costo no encontrado")
        
        # Soft delete
        costo_rigido_service.delete(db=db, obj_id=costo_id)
        
        return {"message": "Costo eliminado exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar costo: {str(e)}")


@router.get("/estadisticas/resumen")
async def obtener_estadisticas_costos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener estadísticas generales de costos rígidos.
    """
    try:
        # Estadísticas generales
        stats_generales = db.query(
            func.count(CostoRigido.id).label("total_costos"),
            func.count().filter(CostoRigido.tipo == "fijo").label("costos_fijos"),
            func.count().filter(CostoRigido.tipo == "variable").label("costos_variables"),
            func.count().filter(CostoRigido.tipo == "recurrente").label("costos_recurrentes"),
            func.sum(CostoRigido.monto).label("monto_total"),
            func.avg(CostoRigido.monto).label("monto_promedio")
        ).filter(CostoRigido.activo == True).first()
        
        # Estadísticas por categoría
        stats_categoria = db.query(
            CostoRigido.categoria,
            func.count(CostoRigido.id).label("cantidad"),
            func.sum(CostoRigido.monto).label("monto_total"),
            func.avg(CostoRigido.monto).label("monto_promedio")
        ).filter(
            CostoRigido.activo == True
        ).group_by(
            CostoRigido.categoria
        ).order_by(
            func.sum(CostoRigido.monto).desc()
        ).all()
        
        # Estadísticas por frecuencia
        stats_frecuencia = db.query(
            CostoRigido.frecuencia,
            func.count(CostoRigido.id).label("cantidad"),
            func.sum(CostoRigido.monto).label("monto_total")
        ).filter(
            CostoRigido.activo == True
        ).group_by(
            CostoRigido.frecuencia
        ).all()
        
        # Costos por proyecto
        stats_proyecto = db.query(
            Proyecto.nombre.label("proyecto_nombre"),
            func.count(CostoRigido.id).label("cantidad_costos"),
            func.sum(CostoRigido.monto).label("monto_total")
        ).join(
            Proyecto, CostoRigido.proyecto_id == Proyecto.id, isouter=True
        ).filter(
            CostoRigido.activo == True
        ).group_by(
            Proyecto.id, Proyecto.nombre
        ).order_by(
            func.sum(CostoRigido.monto).desc()
        ).limit(10).all()
        
        # Costos mensuales (últimos 12 meses)
        costos_mensuales = db.query(
            extract('year', CostoRigido.fecha_aplicacion).label('año'),
            extract('month', CostoRigido.fecha_aplicacion).label('mes'),
            func.count(CostoRigido.id).label('cantidad'),
            func.sum(CostoRigido.valor).label('monto_total')
        ).filter(
            and_(
                CostoRigido.activo == True,
                CostoRigido.fecha_aplicacion >= func.current_date() - func.interval('12 months')
            )
        ).group_by(
            extract('year', CostoRigido.fecha_aplicacion),
            extract('month', CostoRigido.fecha_aplicacion)
        ).order_by(
            extract('year', CostoRigido.fecha_aplicacion),
            extract('month', CostoRigido.fecha_aplicacion)
        ).all()
        
        return {
            "generales": {
                "total_costos": stats_generales.total_costos or 0,
                "por_tipo": {
                    "fijos": stats_generales.costos_fijos or 0,
                    "variables": stats_generales.costos_variables or 0,
                    "recurrentes": stats_generales.costos_recurrentes or 0
                },
                "montos": {
                    "total": float(stats_generales.monto_total or 0),
                    "promedio": float(stats_generales.monto_promedio or 0)
                }
            },
            "por_categoria": [
                {
                    "categoria": row.categoria,
                    "cantidad": row.cantidad,
                    "monto_total": float(row.monto_total or 0),
                    "monto_promedio": float(row.monto_promedio or 0)
                }
                for row in stats_categoria
            ],
            "por_frecuencia": [
                {
                    "frecuencia": row.frecuencia,
                    "cantidad": row.cantidad,
                    "monto_total": float(row.monto_total or 0)
                }
                for row in stats_frecuencia
            ],
            "por_proyecto": [
                {
                    "proyecto": row.proyecto_nombre or "Sin proyecto",
                    "cantidad_costos": row.cantidad_costos,
                    "monto_total": float(row.monto_total or 0)
                }
                for row in stats_proyecto
            ],
            "mensuales": [
                {
                    "año": int(row.año),
                    "mes": int(row.mes),
                    "cantidad": row.cantidad,
                    "monto_total": float(row.monto_total or 0)
                }
                for row in costos_mensuales
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {str(e)}")


@router.get("/categorias/lista")
async def listar_categorias(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener lista de categorías únicas de costos.
    """
    try:
        categorias = db.query(CostoRigido.categoria).filter(
            CostoRigido.activo == True
        ).distinct().all()
        
        return {
            "categorias": [cat[0] for cat in categorias if cat[0]]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener categorías: {str(e)}")


@router.get("/proveedores/lista")
async def listar_proveedores(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener lista de proveedores únicos.
    """
    try:
        proveedores = db.query(CostoRigido.proveedor).filter(
            and_(
                CostoRigido.activo == True,
                CostoRigido.proveedor.is_not(None)
            )
        ).distinct().all()
        
        return {
            "proveedores": [prov[0] for prov in proveedores if prov[0]]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener proveedores: {str(e)}")


@router.get("/calcular-proyeccion")
async def calcular_proyeccion_costos(
    proyecto_id: Optional[int] = Query(None, description="ID del proyecto (opcional)"),
    meses: int = Query(12, ge=1, le=60, description="Número de meses a proyectar"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Calcular proyección de costos para un período determinado.
    """
    try:
        # Construir filtros
        filters = [CostoRigido.activo == True]
        
        if proyecto_id:
            filters.append(CostoRigido.proyecto_id == proyecto_id)
        
        # Obtener costos activos
        costos = db.query(CostoRigido).filter(and_(*filters)).all()
        
        # Calcular proyección
        proyeccion_mensual = []
        total_proyectado = 0
        
        for mes in range(1, meses + 1):
            costo_mes = 0
            
            for costo in costos:
                # Verificar si el costo aplica para este mes
                fecha_actual = date.today().replace(day=1)
                fecha_mes = date(fecha_actual.year, fecha_actual.month + mes - 1, 1)
                
                # Verificar si está en el rango de fechas del costo
                if fecha_mes < costo.fecha_aplicacion:
                    continue
                
                # Sin fecha_fin, el costo se aplica indefinidamente
                
                # Calcular monto según frecuencia
                if costo.frecuencia == "mensual":
                    costo_mes += costo.monto
                elif costo.frecuencia == "trimestral" and mes % 3 == 1:
                    costo_mes += costo.monto
                elif costo.frecuencia == "semestral" and mes % 6 == 1:
                    costo_mes += costo.monto
                elif costo.frecuencia == "anual" and mes == 1:
                    costo_mes += costo.monto
                elif costo.frecuencia == "unico" and mes == 1:
                    costo_mes += costo.monto
            
            proyeccion_mensual.append({
                "mes": mes,
                "fecha": fecha_mes.isoformat(),
                "costo_proyectado": float(costo_mes)
            })
            
            total_proyectado += costo_mes
        
        return {
            "proyecto_id": proyecto_id,
            "periodo_meses": meses,
            "total_proyectado": float(total_proyectado),
            "promedio_mensual": float(total_proyectado / meses) if meses > 0 else 0,
            "detalle_mensual": proyeccion_mensual
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al calcular proyección: {str(e)}")
