from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.auth import get_current_active_user
from app.models import Usuario
from app.schemas.colaborador import (
    ColaboradorCreate, ColaboradorUpdate, ColaboradorResponse, 
    ColaboradorList, EstadisticasColaborador
)
from app.services.colaborador_service import ColaboradorService
import math

router = APIRouter()


@router.post("/", response_model=ColaboradorResponse)
async def create_colaborador(
    colaborador: ColaboradorCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Crear un nuevo colaborador.
    
    Requiere autenticación.
    """
    service = ColaboradorService(db)
    return service.create_colaborador(colaborador)


@router.get("/", response_model=ColaboradorList)
async def read_colaboradores(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo"),
    disponible: Optional[bool] = Query(None, description="Filtrar por disponibilidad"),
    tipo: Optional[str] = Query(None, description="Filtrar por tipo de colaborador"),
    departamento: Optional[str] = Query(None, description="Filtrar por departamento"),
    search: Optional[str] = Query(None, description="Buscar por nombre, apellido o email"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtener lista de colaboradores con filtros y paginación.
    
    Requiere autenticación.
    """
    service = ColaboradorService(db)
    colaboradores, total = service.get_colaboradores(
        skip=skip,
        limit=limit,
        activo=activo,
        disponible=disponible,
        tipo=tipo,
        departamento=departamento,
        search=search
    )
    
    return ColaboradorList(
        colaboradores=colaboradores,
        total=total,
        pagina=skip // limit + 1,
        tamaño_pagina=limit,
        total_paginas=math.ceil(total / limit)
    )


@router.get("/disponibles", response_model=List[ColaboradorResponse])
async def read_colaboradores_disponibles(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtener lista de colaboradores disponibles.
    
    Requiere autenticación.
    """
    service = ColaboradorService(db)
    return service.get_colaboradores_disponibles()


@router.get("/estadisticas", response_model=EstadisticasColaborador)
async def read_estadisticas_colaboradores(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtener estadísticas de colaboradores.
    
    Requiere autenticación.
    """
    service = ColaboradorService(db)
    return service.get_estadisticas()


@router.get("/por-habilidad/{habilidad}", response_model=List[ColaboradorResponse])
async def read_colaboradores_por_habilidad(
    habilidad: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Buscar colaboradores por habilidad.
    
    Requiere autenticación.
    """
    service = ColaboradorService(db)
    return service.buscar_colaboradores_por_habilidad(habilidad)


@router.get("/por-departamento/{departamento}", response_model=List[ColaboradorResponse])
async def read_colaboradores_por_departamento(
    departamento: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtener colaboradores por departamento.
    
    Requiere autenticación.
    """
    service = ColaboradorService(db)
    return service.get_colaboradores_por_departamento(departamento)


@router.get("/{colaborador_id}", response_model=ColaboradorResponse)
async def read_colaborador(
    colaborador_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtener un colaborador por ID.
    
    Requiere autenticación.
    """
    service = ColaboradorService(db)
    colaborador = service.get_colaborador(colaborador_id)
    if colaborador is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Colaborador no encontrado"
        )
    return colaborador


@router.put("/{colaborador_id}", response_model=ColaboradorResponse)
async def update_colaborador(
    colaborador_id: int,
    colaborador: ColaboradorUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Actualizar un colaborador.
    
    Requiere autenticación.
    """
    service = ColaboradorService(db)
    db_colaborador = service.update_colaborador(colaborador_id, colaborador)
    if db_colaborador is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Colaborador no encontrado"
        )
    return db_colaborador


@router.delete("/{colaborador_id}")
async def delete_colaborador(
    colaborador_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Eliminar (desactivar) un colaborador.
    
    Requiere autenticación.
    """
    service = ColaboradorService(db)
    success = service.delete_colaborador(colaborador_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Colaborador no encontrado"
        )
    return {"message": "Colaborador eliminado exitosamente"}


@router.post("/{colaborador_id}/activar", response_model=ColaboradorResponse)
async def activar_colaborador(
    colaborador_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Activar un colaborador.
    
    Requiere autenticación.
    """
    service = ColaboradorService(db)
    db_colaborador = service.activar_colaborador(colaborador_id)
    if db_colaborador is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Colaborador no encontrado"
        )
    return db_colaborador
