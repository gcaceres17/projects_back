from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from fastapi import HTTPException, status
from app.models import Colaborador, proyecto_colaborador
from app.schemas.colaborador import ColaboradorCreate, ColaboradorUpdate, EstadisticasColaborador
import logging

logger = logging.getLogger(__name__)


class ColaboradorService:
    """Servicio para operaciones CRUD de colaboradores."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_colaborador(self, colaborador: ColaboradorCreate) -> Colaborador:
        """
        Crear un nuevo colaborador.
        
        Args:
            colaborador: Datos del colaborador a crear
            
        Returns:
            Colaborador: El colaborador creado
            
        Raises:
            HTTPException: Si el email ya existe
        """
        # Verificar si el email ya existe
        existing_colaborador = self.db.query(Colaborador).filter(
            Colaborador.email == colaborador.email
        ).first()
        if existing_colaborador:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un colaborador con el email {colaborador.email}"
            )
        
        db_colaborador = Colaborador(**colaborador.dict())
        self.db.add(db_colaborador)
        self.db.commit()
        self.db.refresh(db_colaborador)
        
        logger.info(f"Colaborador creado: {db_colaborador.email}")
        return db_colaborador
    
    def get_colaborador(self, colaborador_id: int) -> Optional[Colaborador]:
        """
        Obtener un colaborador por ID.
        
        Args:
            colaborador_id: ID del colaborador
            
        Returns:
            Optional[Colaborador]: El colaborador o None si no existe
        """
        return self.db.query(Colaborador).filter(Colaborador.id == colaborador_id).first()
    
    def get_colaborador_by_email(self, email: str) -> Optional[Colaborador]:
        """
        Obtener un colaborador por email.
        
        Args:
            email: Email del colaborador
            
        Returns:
            Optional[Colaborador]: El colaborador o None si no existe
        """
        return self.db.query(Colaborador).filter(Colaborador.email == email).first()
    
    def get_colaboradores(
        self,
        skip: int = 0,
        limit: int = 100,
        activo: Optional[bool] = None,
        disponible: Optional[bool] = None,
        tipo: Optional[str] = None,
        departamento: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[List[Colaborador], int]:
        """
        Obtener lista de colaboradores con filtros y paginación.
        
        Args:
            skip: Número de registros a saltar
            limit: Número máximo de registros a retornar
            activo: Filtrar por estado activo/inactivo
            disponible: Filtrar por disponibilidad
            tipo: Filtrar por tipo de colaborador
            departamento: Filtrar por departamento
            search: Buscar por nombre, apellido o email
            
        Returns:
            tuple: (lista_colaboradores, total_registros)
        """
        query = self.db.query(Colaborador)
        
        # Aplicar filtros
        if activo is not None:
            query = query.filter(Colaborador.activo == activo)
        
        if disponible is not None:
            query = query.filter(Colaborador.disponible == disponible)
        
        if tipo:
            query = query.filter(Colaborador.tipo == tipo)
        
        if departamento:
            query = query.filter(Colaborador.departamento == departamento)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Colaborador.nombre.ilike(search_term),
                    Colaborador.apellido.ilike(search_term),
                    Colaborador.email.ilike(search_term)
                )
            )
        
        # Contar total de registros
        total = query.count()
        
        # Aplicar paginación
        colaboradores = query.offset(skip).limit(limit).all()
        
        return colaboradores, total
    
    def update_colaborador(
        self, 
        colaborador_id: int, 
        colaborador_update: ColaboradorUpdate
    ) -> Optional[Colaborador]:
        """
        Actualizar un colaborador.
        
        Args:
            colaborador_id: ID del colaborador a actualizar
            colaborador_update: Datos actualizados del colaborador
            
        Returns:
            Optional[Colaborador]: El colaborador actualizado o None si no existe
            
        Raises:
            HTTPException: Si el email ya existe para otro colaborador
        """
        db_colaborador = self.get_colaborador(colaborador_id)
        if not db_colaborador:
            return None
        
        # Verificar email único si se está actualizando
        if colaborador_update.email and colaborador_update.email != db_colaborador.email:
            existing_colaborador = self.db.query(Colaborador).filter(
                and_(
                    Colaborador.email == colaborador_update.email,
                    Colaborador.id != colaborador_id
                )
            ).first()
            if existing_colaborador:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe un colaborador con el email {colaborador_update.email}"
                )
        
        # Actualizar campos
        update_data = colaborador_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_colaborador, field, value)
        
        self.db.commit()
        self.db.refresh(db_colaborador)
        
        logger.info(f"Colaborador actualizado: {db_colaborador.email}")
        return db_colaborador
    
    def delete_colaborador(self, colaborador_id: int) -> bool:
        """
        Eliminar (desactivar) un colaborador.
        
        Args:
            colaborador_id: ID del colaborador a eliminar
            
        Returns:
            bool: True si se eliminó exitosamente, False si no existe
        """
        db_colaborador = self.get_colaborador(colaborador_id)
        if not db_colaborador:
            return False
        
        # Soft delete - solo marcar como inactivo
        db_colaborador.activo = False
        self.db.commit()
        
        logger.info(f"Colaborador desactivado: {db_colaborador.email}")
        return True
    
    def get_estadisticas(self) -> EstadisticasColaborador:
        """
        Obtener estadísticas de colaboradores.
        
        Returns:
            EstadisticasColaborador: Estadísticas de colaboradores
        """
        # Contar colaboradores
        total_colaboradores = self.db.query(Colaborador).count()
        colaboradores_activos = self.db.query(Colaborador).filter(
            Colaborador.activo == True
        ).count()
        colaboradores_disponibles = self.db.query(Colaborador).filter(
            and_(Colaborador.activo == True, Colaborador.disponible == True)
        ).count()
        
        # Calcular promedio de costo por hora
        promedio_costo_hora = self.db.query(func.avg(Colaborador.costo_hora)).scalar() or 0.0
        
        # Agrupar por tipo
        tipos_query = self.db.query(
            Colaborador.tipo,
            func.count(Colaborador.id).label('count')
        ).filter(Colaborador.activo == True).group_by(Colaborador.tipo).all()
        
        total_por_tipo = {str(tipo): count for tipo, count in tipos_query}
        
        # Agrupar por departamento
        departamentos_query = self.db.query(
            Colaborador.departamento,
            func.count(Colaborador.id).label('count')
        ).filter(
            and_(Colaborador.activo == True, Colaborador.departamento.isnot(None))
        ).group_by(Colaborador.departamento).all()
        
        total_por_departamento = {dept: count for dept, count in departamentos_query}
        
        return EstadisticasColaborador(
            total_colaboradores=total_colaboradores,
            colaboradores_activos=colaboradores_activos,
            colaboradores_disponibles=colaboradores_disponibles,
            promedio_costo_hora=round(promedio_costo_hora, 2),
            total_por_tipo=total_por_tipo,
            total_por_departamento=total_por_departamento
        )
    
    def get_colaboradores_disponibles(self) -> List[Colaborador]:
        """
        Obtener lista de colaboradores disponibles.
        
        Returns:
            List[Colaborador]: Lista de colaboradores disponibles
        """
        return self.db.query(Colaborador).filter(
            and_(
                Colaborador.activo == True,
                Colaborador.disponible == True
            )
        ).all()
    
    def buscar_colaboradores_por_habilidad(self, habilidad: str) -> List[Colaborador]:
        """
        Buscar colaboradores por habilidad.
        
        Args:
            habilidad: Habilidad a buscar
            
        Returns:
            List[Colaborador]: Lista de colaboradores con la habilidad
        """
        return self.db.query(Colaborador).filter(
            and_(
                Colaborador.activo == True,
                Colaborador.habilidades.ilike(f"%{habilidad}%")
            )
        ).all()
    
    def get_colaboradores_por_departamento(self, departamento: str) -> List[Colaborador]:
        """
        Obtener colaboradores por departamento.
        
        Args:
            departamento: Nombre del departamento
            
        Returns:
            List[Colaborador]: Lista de colaboradores del departamento
        """
        return self.db.query(Colaborador).filter(
            and_(
                Colaborador.activo == True,
                Colaborador.departamento == departamento
            )
        ).all()
    
    def activar_colaborador(self, colaborador_id: int) -> Optional[Colaborador]:
        """
        Activar un colaborador.
        
        Args:
            colaborador_id: ID del colaborador a activar
            
        Returns:
            Optional[Colaborador]: El colaborador activado o None si no existe
        """
        db_colaborador = self.get_colaborador(colaborador_id)
        if not db_colaborador:
            return None
        
        db_colaborador.activo = True
        self.db.commit()
        self.db.refresh(db_colaborador)
        
        logger.info(f"Colaborador activado: {db_colaborador.email}")
        return db_colaborador
