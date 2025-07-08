"""
Router para gestión de cotizaciones
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime, date

from app.database import get_db
from app.auth import get_current_user
from app.models import Cotizacion, CotizacionItem, Usuario, Cliente, Proyecto
from app.schemas import (
    CotizacionCreate, CotizacionUpdate, CotizacionResponse, 
    CotizacionItemCreate, PaginatedResponse
)
from app.services.cotizacion_service import cotizacion_service

router = APIRouter(prefix="/cotizaciones", tags=["cotizaciones"])

# El servicio se importa directamente desde cotizacion_service


def generar_numero_cotizacion(db: Session) -> str:
    """
    Generar número único para la cotización.
    """
    year = datetime.now().year
    month = datetime.now().month
    
    # Buscar el último número del mes actual
    last_cotizacion = db.query(Cotizacion).filter(
        Cotizacion.numero.like(f"COT-{year:04d}{month:02d}-%")
    ).order_by(Cotizacion.numero.desc()).first()
    
    if last_cotizacion:
        # Extraer el número secuencial y incrementar
        last_number = int(last_cotizacion.numero.split("-")[-1])
        new_number = last_number + 1
    else:
        new_number = 1
    
    return f"COT-{year:04d}{month:02d}-{new_number:04d}"


def calcular_totales_cotizacion(items: List[CotizacionItemCreate]) -> dict:
    """
    Calcular subtotal, impuestos y total de la cotización.
    """
    subtotal = sum(item.cantidad * item.precio_unitario for item in items)
    
    # IVA del 19% (configurable)
    iva_porcentaje = 0.19
    impuestos = subtotal * iva_porcentaje
    
    total = subtotal + impuestos
    
    return {
        "subtotal": subtotal,
        "impuestos": impuestos,
        "total": total
    }


@router.get("", response_model=PaginatedResponse[CotizacionResponse])
async def listar_cotizaciones(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(10, ge=1, le=100, description="Número de registros a devolver"),
    cliente_id: Optional[int] = Query(None, description="Filtrar por cliente"),
    proyecto_id: Optional[int] = Query(None, description="Filtrar por proyecto"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    fecha_desde: Optional[date] = Query(None, description="Filtrar desde fecha"),
    fecha_hasta: Optional[date] = Query(None, description="Filtrar hasta fecha"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Listar cotizaciones con paginación y filtros.
    """
    try:
        # Construir filtros
        filters = [Cotizacion.activo == True]
        
        if cliente_id:
            filters.append(Cotizacion.cliente_id == cliente_id)
        
        if proyecto_id:
            filters.append(Cotizacion.proyecto_id == proyecto_id)
        
        if estado:
            filters.append(Cotizacion.estado == estado)
        
        if fecha_desde:
            filters.append(Cotizacion.fecha_cotizacion >= fecha_desde)
        
        if fecha_hasta:
            filters.append(Cotizacion.fecha_cotizacion <= fecha_hasta)
        
        # Obtener datos paginados
        result = cotizacion_service.get_paginated(
            db=db,
            skip=skip,
            limit=limit,
            filters=filters,
            order_by=[Cotizacion.fecha_cotizacion.desc()]
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener cotizaciones: {str(e)}")


@router.post("", response_model=CotizacionResponse, status_code=201)
async def crear_cotizacion(
    cotizacion_data: CotizacionCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Crear una nueva cotización con sus items.
    """
    try:
        # Verificar que el cliente existe
        cliente = db.query(Cliente).filter(Cliente.id == cotizacion_data.cliente_id).first()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        # Verificar que el proyecto existe (si se especifica)
        if cotizacion_data.proyecto_id:
            proyecto = db.query(Proyecto).filter(Proyecto.id == cotizacion_data.proyecto_id).first()
            if not proyecto:
                raise HTTPException(status_code=404, detail="Proyecto no encontrado")
        
        # Calcular totales
        totales = calcular_totales_cotizacion(cotizacion_data.items)
        
        # Generar número de cotización
        numero = generar_numero_cotizacion(db)
        
        # Crear cotización
        cotizacion_dict = cotizacion_data.dict(exclude={"items"})
        cotizacion_dict.update({
            "numero": numero,
            "subtotal": totales["subtotal"],
            "impuestos": totales["impuestos"],
            "total": totales["total"]
        })
        
        cotizacion = Cotizacion(**cotizacion_dict)
        db.add(cotizacion)
        db.flush()  # Para obtener el ID
        
        # Crear items de la cotizacion
        for idx, item_data in enumerate(cotizacion_data.items):
            item = CotizacionItem(
                cotizacion_id=cotizacion.id,
                descripcion=item_data.descripcion,
                cantidad=item_data.cantidad,
                precio_unitario=item_data.precio_unitario,
                subtotal=item_data.cantidad * item_data.precio_unitario,
                orden=idx + 1
            )
            db.add(item)
        
        db.commit()
        db.refresh(cotizacion)
        
        return cotizacion
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear cotización: {str(e)}")


@router.get("/{cotizacion_id}", response_model=CotizacionResponse)
async def obtener_cotizacion(
    cotizacion_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener cotización por ID con sus items.
    """
    try:
        cotizacion = db.query(Cotizacion).filter(
            and_(
                Cotizacion.id == cotizacion_id,
                Cotizacion.activo == True
            )
        ).first()
        
        if not cotizacion:
            raise HTTPException(status_code=404, detail="Cotización no encontrada")
        
        return cotizacion
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener cotización: {str(e)}")


@router.put("/{cotizacion_id}", response_model=CotizacionResponse)
async def actualizar_cotizacion(
    cotizacion_id: int,
    cotizacion_data: CotizacionUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Actualizar cotización existente.
    """
    try:
        # Verificar que la cotización existe
        cotizacion = db.query(Cotizacion).filter(
            and_(
                Cotizacion.id == cotizacion_id,
                Cotizacion.activo == True
            )
        ).first()
        
        if not cotizacion:
            raise HTTPException(status_code=404, detail="Cotización no encontrada")
        
        # Solo permitir actualización si está en estado borrador
        if cotizacion.estado != "borrador":
            raise HTTPException(
                status_code=400, 
                detail="Solo se pueden actualizar cotizaciones en estado borrador"
            )
        
        # Actualizar campos
        update_data = cotizacion_data.dict(exclude_unset=True, exclude={"items"})
        for field, value in update_data.items():
            setattr(cotizacion, field, value)
        
        # Si se proporcionan items, recalcular y actualizar
        if cotizacion_data.items is not None:
            # Eliminar items existentes
            db.query(CotizacionItem).filter(
                CotizacionItem.cotizacion_id == cotizacion_id
            ).delete()
            
            # Calcular nuevos totales
            totales = calcular_totales_cotizacion(cotizacion_data.items)
            cotizacion.subtotal = totales["subtotal"]
            cotizacion.impuestos = totales["impuestos"]
            cotizacion.total = totales["total"]
            
            # Crear nuevos items
            for idx, item_data in enumerate(cotizacion_data.items):
                item = CotizacionItem(
                    cotizacion_id=cotizacion.id,
                    descripcion=item_data.descripcion,
                    cantidad=item_data.cantidad,
                    precio_unitario=item_data.precio_unitario,
                    subtotal=item_data.cantidad * item_data.precio_unitario,
                    orden=idx + 1
                )
                db.add(item)
        
        db.commit()
        db.refresh(cotizacion)
        
        return cotizacion
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar cotización: {str(e)}")


@router.patch("/{cotizacion_id}/estado")
async def cambiar_estado_cotizacion(
    cotizacion_id: int,
    nuevo_estado: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Cambiar el estado de una cotización.
    """
    try:
        # Estados válidos
        estados_validos = ["borrador", "enviada", "revisada", "aprobada", "rechazada", "cancelada"]
        
        if nuevo_estado not in estados_validos:
            raise HTTPException(
                status_code=400, 
                detail=f"Estado inválido. Estados válidos: {', '.join(estados_validos)}"
            )
        
        # Verificar que la cotización existe
        cotizacion = db.query(Cotizacion).filter(
            and_(
                Cotizacion.id == cotizacion_id,
                Cotizacion.activo == True
            )
        ).first()
        
        if not cotizacion:
            raise HTTPException(status_code=404, detail="Cotización no encontrada")
        
        # Actualizar estado
        cotizacion.estado = nuevo_estado
        cotizacion.fecha_actualizacion = datetime.utcnow()
        
        db.commit()
        
        return {
            "message": f"Estado de cotización actualizado a: {nuevo_estado}",
            "cotizacion_id": cotizacion_id,
            "nuevo_estado": nuevo_estado
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al cambiar estado: {str(e)}")


@router.delete("/{cotizacion_id}")
async def eliminar_cotizacion(
    cotizacion_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Eliminar cotización (soft delete).
    """
    try:
        # Verificar que la cotización existe
        cotizacion = db.query(Cotizacion).filter(
            and_(
                Cotizacion.id == cotizacion_id,
                Cotizacion.activo == True
            )
        ).first()
        
        if not cotizacion:
            raise HTTPException(status_code=404, detail="Cotización no encontrada")
        
        # Solo permitir eliminación si está en estado borrador
        if cotizacion.estado != "borrador":
            raise HTTPException(
                status_code=400, 
                detail="Solo se pueden eliminar cotizaciones en estado borrador"
            )
        
        # Soft delete
        cotizacion.activo = False
        cotizacion.fecha_actualizacion = datetime.utcnow()
        
        db.commit()
        
        return {"message": "Cotización eliminada exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar cotización: {str(e)}")


@router.get("/estadisticas/resumen")
async def obtener_estadisticas_cotizaciones(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener estadísticas generales de cotizaciones.
    """
    try:
        from sqlalchemy import sum as sql_sum
        
        # Estadísticas generales
        stats = db.query(
            func.count(Cotizacion.id).label("total"),
            func.count().filter(Cotizacion.estado == "borrador").label("borradores"),
            func.count().filter(Cotizacion.estado == "enviada").label("enviadas"),
            func.count().filter(Cotizacion.estado == "aprobada").label("aprobadas"),
            func.count().filter(Cotizacion.estado == "rechazada").label("rechazadas"),
            sql_sum(Cotizacion.total).label("valor_total"),
            sql_sum(Cotizacion.total).filter(Cotizacion.estado == "aprobada").label("valor_aprobado")
        ).filter(Cotizacion.activo == True).first()
        
        # Cotizaciones por mes (últimos 6 meses)
        cotizaciones_mensuales = db.query(
            func.extract('year', Cotizacion.fecha_cotizacion).label('año'),
            func.extract('month', Cotizacion.fecha_cotizacion).label('mes'),
            func.count(Cotizacion.id).label('cantidad'),
            sql_sum(Cotizacion.total).label('valor')
        ).filter(
            and_(
                Cotizacion.activo == True,
                Cotizacion.fecha_cotizacion >= func.current_date() - func.interval('6 months')
            )
        ).group_by(
            func.extract('year', Cotizacion.fecha_cotizacion),
            func.extract('month', Cotizacion.fecha_cotizacion)
        ).order_by(
            func.extract('year', Cotizacion.fecha_cotizacion),
            func.extract('month', Cotizacion.fecha_cotizacion)
        ).all()
        
        return {
            "generales": {
                "total": stats.total or 0,
                "por_estado": {
                    "borradores": stats.borradores or 0,
                    "enviadas": stats.enviadas or 0,
                    "aprobadas": stats.aprobadas or 0,
                    "rechazadas": stats.rechazadas or 0
                },
                "valores": {
                    "total": float(stats.valor_total or 0),
                    "aprobado": float(stats.valor_aprobado or 0)
                }
            },
            "mensuales": [
                {
                    "año": int(row.año),
                    "mes": int(row.mes),
                    "cantidad": row.cantidad,
                    "valor": float(row.valor or 0)
                }
                for row in cotizaciones_mensuales
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {str(e)}")
