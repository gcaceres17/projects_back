from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from fastapi import HTTPException, status
from app.models import Proyecto, Cliente, Colaborador, proyecto_colaborador
from app.schemas.proyecto import ProyectoCreate, ProyectoUpdate, EstadisticasProyecto
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ProyectoService:
    """Servicio para operaciones CRUD de proyectos."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_proyecto(self, proyecto: ProyectoCreate) -> Proyecto:
        """
        Crear un nuevo proyecto.
        
        Args:
            proyecto: Datos del proyecto a crear
            
        Returns:
            Proyecto: El proyecto creado
            
        Raises:
            HTTPException: Si el cliente no existe
        """
        # Verificar que el cliente existe
        cliente = self.db.query(Cliente).filter(Cliente.id == proyecto.cliente_id).first()
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No existe un cliente con ID {proyecto.cliente_id}"
            )
        
        # Crear el proyecto
        proyecto_data = proyecto.dict(exclude={'colaboradores_ids'})
        db_proyecto = Proyecto(**proyecto_data)
        self.db.add(db_proyecto)
        self.db.flush()  # Para obtener el ID del proyecto
        
        # Asignar colaboradores si se especificaron
        if proyecto.colaboradores_ids:
            for colaborador_id in proyecto.colaboradores_ids:
                colaborador = self.db.query(Colaborador).filter(
                    Colaborador.id == colaborador_id
                ).first()
                if colaborador:
                    db_proyecto.colaboradores.append(colaborador)
        
        self.db.commit()
        self.db.refresh(db_proyecto)
        
        logger.info(f"Proyecto creado: {db_proyecto.nombre}")
        return db_proyecto
    
    def get_proyecto(self, proyecto_id: int) -> Optional[Proyecto]:
        """
        Obtener un proyecto por ID.
        
        Args:
            proyecto_id: ID del proyecto
            
        Returns:
            Optional[Proyecto]: El proyecto o None si no existe
        """
        return self.db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    
    def get_proyectos(
        self,
        skip: int = 0,
        limit: int = 100,
        activo: Optional[bool] = None,
        estado: Optional[str] = None,
        cliente_id: Optional[int] = None,
        search: Optional[str] = None
    ) -> tuple[List[Proyecto], int]:
        """
        Obtener lista de proyectos con filtros y paginación.
        
        Args:
            skip: Número de registros a saltar
            limit: Número máximo de registros a retornar
            activo: Filtrar por estado activo/inactivo
            estado: Filtrar por estado del proyecto
            cliente_id: Filtrar por cliente
            search: Buscar por nombre del proyecto
            
        Returns:
            tuple: (lista_proyectos, total_registros)
        """
        query = self.db.query(Proyecto)
        
        # Aplicar filtros
        if activo is not None:
            query = query.filter(Proyecto.activo == activo)
        
        if estado:
            query = query.filter(Proyecto.estado == estado)
        
        if cliente_id:
            query = query.filter(Proyecto.cliente_id == cliente_id)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(Proyecto.nombre.ilike(search_term))
        
        # Contar total de registros
        total = query.count()
        
        # Aplicar paginación
        proyectos = query.offset(skip).limit(limit).all()
        
        return proyectos, total
    
    def update_proyecto(
        self, 
        proyecto_id: int, 
        proyecto_update: ProyectoUpdate
    ) -> Optional[Proyecto]:
        """
        Actualizar un proyecto.
        
        Args:
            proyecto_id: ID del proyecto a actualizar
            proyecto_update: Datos actualizados del proyecto
            
        Returns:
            Optional[Proyecto]: El proyecto actualizado o None si no existe
            
        Raises:
            HTTPException: Si el cliente no existe
        """
        db_proyecto = self.get_proyecto(proyecto_id)
        if not db_proyecto:
            return None
        
        # Verificar que el cliente existe si se está actualizando
        if proyecto_update.cliente_id:
            cliente = self.db.query(Cliente).filter(
                Cliente.id == proyecto_update.cliente_id
            ).first()
            if not cliente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"No existe un cliente con ID {proyecto_update.cliente_id}"
                )
        
        # Actualizar campos
        update_data = proyecto_update.dict(exclude_unset=True, exclude={'colaboradores_ids'})
        for field, value in update_data.items():
            setattr(db_proyecto, field, value)
        
        # Actualizar colaboradores si se especificaron
        if proyecto_update.colaboradores_ids is not None:
            # Limpiar colaboradores actuales
            db_proyecto.colaboradores.clear()
            # Agregar nuevos colaboradores
            for colaborador_id in proyecto_update.colaboradores_ids:
                colaborador = self.db.query(Colaborador).filter(
                    Colaborador.id == colaborador_id
                ).first()
                if colaborador:
                    db_proyecto.colaboradores.append(colaborador)
        
        self.db.commit()
        self.db.refresh(db_proyecto)
        
        logger.info(f"Proyecto actualizado: {db_proyecto.nombre}")
        return db_proyecto
    
    def delete_proyecto(self, proyecto_id: int) -> bool:
        """
        Eliminar (desactivar) un proyecto.
        
        Args:
            proyecto_id: ID del proyecto a eliminar
            
        Returns:
            bool: True si se eliminó exitosamente, False si no existe
        """
        db_proyecto = self.get_proyecto(proyecto_id)
        if not db_proyecto:
            return False
        
        # Soft delete - solo marcar como inactivo
        db_proyecto.activo = False
        self.db.commit()
        
        logger.info(f"Proyecto desactivado: {db_proyecto.nombre}")
        return True
    
    def get_estadisticas(self) -> EstadisticasProyecto:
        """
        Obtener estadísticas de proyectos.
        
        Returns:
            EstadisticasProyecto: Estadísticas de proyectos
        """
        # Contar proyectos
        total_proyectos = self.db.query(Proyecto).count()
        proyectos_activos = self.db.query(Proyecto).filter(
            Proyecto.activo == True
        ).count()
        proyectos_completados = self.db.query(Proyecto).filter(
            Proyecto.estado == 'completado'
        ).count()
        proyectos_en_progreso = self.db.query(Proyecto).filter(
            Proyecto.estado == 'en_progreso'
        ).count()
        
        # Calcular totales financieros
        presupuesto_total = self.db.query(func.sum(Proyecto.presupuesto)).scalar() or 0.0
        costo_total = self.db.query(func.sum(Proyecto.costo_real)).scalar() or 0.0
        
        # Calcular promedio de progreso
        promedio_progreso = self.db.query(func.avg(Proyecto.progreso)).scalar() or 0.0
        
        # Agrupar por estado
        estados_query = self.db.query(
            Proyecto.estado,
            func.count(Proyecto.id).label('count')
        ).filter(Proyecto.activo == True).group_by(Proyecto.estado).all()
        
        proyectos_por_estado = {str(estado): count for estado, count in estados_query}
        
        # Agrupar por cliente
        clientes_query = self.db.query(
            Cliente.nombre,
            func.count(Proyecto.id).label('count')
        ).join(Proyecto).filter(Proyecto.activo == True).group_by(Cliente.nombre).all()
        
        proyectos_por_cliente = {cliente: count for cliente, count in clientes_query}
        
        return EstadisticasProyecto(
            total_proyectos=total_proyectos,
            proyectos_activos=proyectos_activos,
            proyectos_completados=proyectos_completados,
            proyectos_en_progreso=proyectos_en_progreso,
            presupuesto_total=presupuesto_total,
            costo_total=costo_total,
            promedio_progreso=round(promedio_progreso, 2),
            proyectos_por_estado=proyectos_por_estado,
            proyectos_por_cliente=proyectos_por_cliente
        )
    
    def asignar_colaborador(
        self, 
        proyecto_id: int, 
        colaborador_id: int, 
        horas_asignadas: float = 0.0
    ) -> Optional[Proyecto]:
        """
        Asignar un colaborador a un proyecto.
        
        Args:
            proyecto_id: ID del proyecto
            colaborador_id: ID del colaborador
            horas_asignadas: Horas asignadas al colaborador
            
        Returns:
            Optional[Proyecto]: El proyecto actualizado o None si no existe
        """
        db_proyecto = self.get_proyecto(proyecto_id)
        if not db_proyecto:
            return None
        
        colaborador = self.db.query(Colaborador).filter(
            Colaborador.id == colaborador_id
        ).first()
        if not colaborador:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No existe un colaborador con ID {colaborador_id}"
            )
        
        # Verificar si ya está asignado
        if colaborador in db_proyecto.colaboradores:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El colaborador ya está asignado a este proyecto"
            )
        
        # Asignar colaborador
        db_proyecto.colaboradores.append(colaborador)
        self.db.commit()
        self.db.refresh(db_proyecto)
        
        logger.info(f"Colaborador {colaborador.email} asignado al proyecto {db_proyecto.nombre}")
        return db_proyecto
    
    def desasignar_colaborador(
        self, 
        proyecto_id: int, 
        colaborador_id: int
    ) -> Optional[Proyecto]:
        """
        Desasignar un colaborador de un proyecto.
        
        Args:
            proyecto_id: ID del proyecto
            colaborador_id: ID del colaborador
            
        Returns:
            Optional[Proyecto]: El proyecto actualizado o None si no existe
        """
        db_proyecto = self.get_proyecto(proyecto_id)
        if not db_proyecto:
            return None
        
        colaborador = self.db.query(Colaborador).filter(
            Colaborador.id == colaborador_id
        ).first()
        if not colaborador:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No existe un colaborador con ID {colaborador_id}"
            )
        
        # Verificar si está asignado
        if colaborador not in db_proyecto.colaboradores:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El colaborador no está asignado a este proyecto"
            )
        
        # Desasignar colaborador
        db_proyecto.colaboradores.remove(colaborador)
        self.db.commit()
        self.db.refresh(db_proyecto)
        
        logger.info(f"Colaborador {colaborador.email} desasignado del proyecto {db_proyecto.nombre}")
        return db_proyecto
    
    def get_proyectos_por_colaborador(self, colaborador_id: int) -> List[Proyecto]:
        """
        Obtener proyectos asignados a un colaborador.
        
        Args:
            colaborador_id: ID del colaborador
            
        Returns:
            List[Proyecto]: Lista de proyectos asignados
        """
        return self.db.query(Proyecto).join(
            proyecto_colaborador
        ).filter(
            proyecto_colaborador.c.colaborador_id == colaborador_id
        ).all()
    
    def get_proyectos_por_cliente(self, cliente_id: int) -> List[Proyecto]:
        """
        Obtener proyectos de un cliente.
        
        Args:
            cliente_id: ID del cliente
            
        Returns:
            List[Proyecto]: Lista de proyectos del cliente
        """
        return self.db.query(Proyecto).filter(
            Proyecto.cliente_id == cliente_id
        ).all()
    
    def actualizar_progreso(self, proyecto_id: int, progreso: float) -> Optional[Proyecto]:
        """
        Actualizar el progreso de un proyecto.
        
        Args:
            proyecto_id: ID del proyecto
            progreso: Nuevo progreso (0-100)
            
        Returns:
            Optional[Proyecto]: El proyecto actualizado o None si no existe
        """
        db_proyecto = self.get_proyecto(proyecto_id)
        if not db_proyecto:
            return None
        
        if progreso < 0 or progreso > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El progreso debe estar entre 0 y 100"
            )
        
        db_proyecto.progreso = progreso
        
        # Si el progreso es 100%, marcar como completado
        if progreso == 100:
            db_proyecto.estado = 'completado'
            db_proyecto.fecha_fin_real = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_proyecto)
        
        logger.info(f"Progreso del proyecto {db_proyecto.nombre} actualizado a {progreso}%")
        return db_proyecto
