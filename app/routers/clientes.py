"""
Router para gestión de clientes
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.database import get_db
from app.auth import get_current_user
from app.models import Cliente, Usuario
from app.schemas import ClienteCreate, ClienteUpdate, ClienteResponse, PaginatedResponse
from app.services.cliente_service import cliente_service

router = APIRouter(prefix="/clientes", tags=["clientes"])

# El servicio se importa directamente desde cliente_service


@router.get("", response_model=PaginatedResponse[ClienteResponse])
async def listar_clientes(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(10, ge=1, le=100, description="Número de registros a devolver"),
    search: Optional[str] = Query(None, description="Buscar por nombre"),
    tipo_cliente: Optional[str] = Query(None, description="Filtrar por tipo de cliente"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Listar clientes con paginación y filtros.
    """
    try:
        # Construir filtros
        filters = []
        
        if search:
            filters.append(Cliente.nombre.ilike(f"%{search}%"))
        
        if tipo_cliente:
            filters.append(Cliente.tipo_cliente == tipo_cliente)
            
        if activo is not None:
            filters.append(Cliente.activo == activo)
        
        # Obtener datos paginados
        result = cliente_service.get_paginated(
            db=db,
            skip=skip,
            limit=limit,
            filters=filters
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener clientes: {str(e)}")


@router.post("", response_model=ClienteResponse, status_code=201)
async def crear_cliente(
    cliente_data: ClienteCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Crear un nuevo cliente.
    """
    try:
        # Verificar que no exista un cliente con el mismo email
        if cliente_data.email:
            existing = db.query(Cliente).filter(Cliente.email == cliente_data.email).first()
            if existing:
                raise HTTPException(
                    status_code=400, 
                    detail="Ya existe un cliente con este email"
                )
        
        # Crear cliente
        cliente = cliente_service.create(db=db, obj_data=cliente_data.dict())
        
        return cliente
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear cliente: {str(e)}")


@router.get("/{cliente_id}", response_model=ClienteResponse)
async def obtener_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener cliente por ID.
    """
    try:
        cliente = cliente_service.get_by_id(db=db, obj_id=cliente_id)
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        return cliente
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener cliente: {str(e)}")


@router.put("/{cliente_id}", response_model=ClienteResponse)
async def actualizar_cliente(
    cliente_id: int,
    cliente_data: ClienteUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Actualizar cliente existente.
    """
    try:
        # Verificar que el cliente existe
        cliente_existente = cliente_service.get_by_id(db=db, obj_id=cliente_id)
        if not cliente_existente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        # Verificar email único si se está actualizando
        if cliente_data.email and cliente_data.email != cliente_existente.email:
            existing = db.query(Cliente).filter(
                and_(
                    Cliente.email == cliente_data.email,
                    Cliente.id != cliente_id
                )
            ).first()
            if existing:
                raise HTTPException(
                    status_code=400, 
                    detail="Ya existe otro cliente con este email"
                )
        
        # Actualizar cliente
        cliente = cliente_service.update(
            db=db, 
            obj_id=cliente_id, 
            obj_data=cliente_data.dict(exclude_unset=True)
        )
        
        return cliente
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar cliente: {str(e)}")


@router.delete("/{cliente_id}")
async def eliminar_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Eliminar cliente (soft delete).
    """
    try:
        # Verificar que el cliente existe
        cliente = cliente_service.get_by_id(db=db, obj_id=cliente_id)
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        # Soft delete
        cliente_service.delete(db=db, obj_id=cliente_id)
        
        return {"message": "Cliente eliminado exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar cliente: {str(e)}")


@router.get("/{cliente_id}/proyectos")
async def obtener_proyectos_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener proyectos de un cliente específico.
    """
    try:
        # Verificar que el cliente existe
        cliente = cliente_service.get_by_id(db=db, obj_id=cliente_id)
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        # Obtener proyectos del cliente
        from app.models import Proyecto
        proyectos = db.query(Proyecto).filter(
            and_(
                Proyecto.cliente_id == cliente_id,
                Proyecto.activo == True
            )
        ).all()
        
        return {
            "cliente": cliente.nombre,
            "proyectos": proyectos
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener proyectos: {str(e)}")


@router.get("/{cliente_id}/estadisticas")
async def obtener_estadisticas_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener estadísticas de un cliente específico.
    """
    try:
        # Verificar que el cliente existe
        cliente = cliente_service.get_by_id(db=db, obj_id=cliente_id)
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        from app.models import Proyecto, Cotizacion
        from sqlalchemy import func, sum as sql_sum
        
        # Estadísticas de proyectos
        proyectos_stats = db.query(
            func.count(Proyecto.id).label("total_proyectos"),
            func.count().filter(Proyecto.estado == "completado").label("proyectos_completados"),
            func.count().filter(Proyecto.estado == "en_progreso").label("proyectos_en_progreso"),
            sql_sum(Proyecto.presupuesto).label("presupuesto_total"),
            sql_sum(Proyecto.costo_real).label("costo_real_total")
        ).filter(
            and_(
                Proyecto.cliente_id == cliente_id,
                Proyecto.activo == True
            )
        ).first()
        
        # Estadísticas de cotizaciones
        cotizaciones_stats = db.query(
            func.count(Cotizacion.id).label("total_cotizaciones"),
            func.count().filter(Cotizacion.estado == "aprobada").label("cotizaciones_aprobadas"),
            sql_sum(Cotizacion.total).label("valor_total_cotizaciones")
        ).filter(
            and_(
                Cotizacion.cliente_id == cliente_id,
                Cotizacion.activo == True
            )
        ).first()
        
        return {
            "cliente": {
                "id": cliente.id,
                "nombre": cliente.nombre,
                "tipo_cliente": cliente.tipo_cliente
            },
            "proyectos": {
                "total": proyectos_stats.total_proyectos or 0,
                "completados": proyectos_stats.proyectos_completados or 0,
                "en_progreso": proyectos_stats.proyectos_en_progreso or 0,
                "presupuesto_total": float(proyectos_stats.presupuesto_total or 0),
                "costo_real_total": float(proyectos_stats.costo_real_total or 0)
            },
            "cotizaciones": {
                "total": cotizaciones_stats.total_cotizaciones or 0,
                "aprobadas": cotizaciones_stats.cotizaciones_aprobadas or 0,
                "valor_total": float(cotizaciones_stats.valor_total_cotizaciones or 0)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {str(e)}")
