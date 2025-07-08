from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.auth import get_current_active_user
from app.models import Usuario
from app.schemas.proyecto import (
    ProyectoCreate, ProyectoUpdate, ProyectoResponse, 
    ProyectoList, EstadisticasProyecto, AsignarColaborador
)
from app.services.proyecto_service import ProyectoService
import math

router = APIRouter()


@router.post("/", response_model=ProyectoResponse)
async def create_proyecto(
    proyecto: ProyectoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Crear un nuevo proyecto.
    
    Requiere autenticación.
    """
    service = ProyectoService(db)
    return service.create_proyecto(proyecto)


@router.get("/", response_model=ProyectoList)
async def read_proyectos(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo"),
    estado: Optional[str] = Query(None, description="Filtrar por estado del proyecto"),
    cliente_id: Optional[int] = Query(None, description="Filtrar por cliente"),
    search: Optional[str] = Query(None, description="Buscar por nombre del proyecto"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtener lista de proyectos con filtros y paginación.
    
    Requiere autenticación.
    """
    service = ProyectoService(db)
    proyectos, total = service.get_proyectos(
        skip=skip,
        limit=limit,
        activo=activo,
        estado=estado,
        cliente_id=cliente_id,
        search=search
    )
    
    return ProyectoList(
        proyectos=proyectos,
        total=total,
        pagina=skip // limit + 1,
        tamaño_pagina=limit,
        total_paginas=math.ceil(total / limit)
    )


@router.get("/estadisticas", response_model=EstadisticasProyecto)
async def read_estadisticas_proyectos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtener estadísticas de proyectos.
    
    Requiere autenticación.
    """
    service = ProyectoService(db)
    return service.get_estadisticas()


@router.get("/por-colaborador/{colaborador_id}", response_model=List[ProyectoResponse])
async def read_proyectos_por_colaborador(
    colaborador_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtener proyectos asignados a un colaborador.
    
    Requiere autenticación.
    """
    service = ProyectoService(db)
    return service.get_proyectos_por_colaborador(colaborador_id)


@router.get("/por-cliente/{cliente_id}", response_model=List[ProyectoResponse])
async def read_proyectos_por_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtener proyectos de un cliente.
    
    Requiere autenticación.
    """
    service = ProyectoService(db)
    return service.get_proyectos_por_cliente(cliente_id)


@router.get("/{proyecto_id}", response_model=ProyectoResponse)
async def read_proyecto(
    proyecto_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtener un proyecto por ID.
    
    Requiere autenticación.
    """
    service = ProyectoService(db)
    proyecto = service.get_proyecto(proyecto_id)
    if proyecto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    return proyecto


@router.put("/{proyecto_id}", response_model=ProyectoResponse)
async def update_proyecto(
    proyecto_id: int,
    proyecto: ProyectoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Actualizar un proyecto.
    
    Requiere autenticación.
    """
    service = ProyectoService(db)
    db_proyecto = service.update_proyecto(proyecto_id, proyecto)
    if db_proyecto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    return db_proyecto


@router.delete("/{proyecto_id}")
async def delete_proyecto(
    proyecto_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Eliminar (desactivar) un proyecto.
    
    Requiere autenticación.
    """
    service = ProyectoService(db)
    success = service.delete_proyecto(proyecto_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    return {"message": "Proyecto eliminado exitosamente"}


@router.post("/{proyecto_id}/asignar-colaborador", response_model=ProyectoResponse)
async def asignar_colaborador(
    proyecto_id: int,
    asignacion: AsignarColaborador,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Asignar un colaborador a un proyecto.
    
    Requiere autenticación.
    """
    service = ProyectoService(db)
    db_proyecto = service.asignar_colaborador(
        proyecto_id, 
        asignacion.colaborador_id, 
        asignacion.horas_asignadas
    )
    if db_proyecto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    return db_proyecto


@router.delete("/{proyecto_id}/desasignar-colaborador/{colaborador_id}")
async def desasignar_colaborador(
    proyecto_id: int,
    colaborador_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Desasignar un colaborador de un proyecto.
    
    Requiere autenticación.
    """
    service = ProyectoService(db)
    db_proyecto = service.desasignar_colaborador(proyecto_id, colaborador_id)
    if db_proyecto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    return {"message": "Colaborador desasignado exitosamente"}


@router.patch("/{proyecto_id}/progreso")
async def actualizar_progreso(
    proyecto_id: int,
    progreso: float = Query(..., ge=0, le=100, description="Progreso del proyecto (0-100)"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Actualizar el progreso de un proyecto.
    
    Requiere autenticación.
    """
    service = ProyectoService(db)
    db_proyecto = service.actualizar_progreso(proyecto_id, progreso)
    if db_proyecto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    return {"message": f"Progreso actualizado a {progreso}%", "proyecto": db_proyecto}
