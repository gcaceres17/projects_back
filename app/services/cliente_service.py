"""
Servicio para gestión de clientes.

Este módulo contiene la lógica de negocio específica para clientes.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.models import Cliente, Proyecto, Cotizacion
from app.schemas.cliente import ClienteCreate, ClienteUpdate
from app.services.base_service import BaseService


class ClienteService(BaseService[Cliente, ClienteCreate, ClienteUpdate]):
    """
    Servicio para operaciones específicas de clientes.
    """
    
    def __init__(self):
        super().__init__(Cliente)
    
    def get_by_email(self, db: Session, *, email: str) -> Optional[Cliente]:
        """
        Obtener cliente por email.
        
        Args:
            db: Sesión de base de datos
            email: Email del cliente
            
        Returns:
            Cliente encontrado o None si no existe
        """
        return db.query(Cliente).filter(Cliente.email == email).first()
    
    def get_by_tipo(
        self,
        db: Session,
        *,
        tipo_cliente: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Cliente]:
        """
        Obtener clientes por tipo.
        
        Args:
            db: Sesión de base de datos
            tipo_cliente: Tipo de cliente
            skip: Número de registros a omitir
            limit: Número máximo de registros a devolver
            
        Returns:
            Lista de clientes
        """
        return db.query(Cliente).filter(
            Cliente.tipo_cliente == tipo_cliente
        ).offset(skip).limit(limit).all()
    
    def search_by_name(
        self,
        db: Session,
        *,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Cliente]:
        """
        Buscar clientes por nombre.
        
        Args:
            db: Sesión de base de datos
            search_term: Término de búsqueda
            skip: Número de registros a omitir
            limit: Número máximo de registros a devolver
            
        Returns:
            Lista de clientes que coinciden con la búsqueda
        """
        return db.query(Cliente).filter(
            Cliente.nombre.ilike(f"%{search_term}%")
        ).offset(skip).limit(limit).all()
    
    def get_with_projects(self, db: Session, *, cliente_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtener cliente con sus proyectos.
        
        Args:
            db: Sesión de base de datos
            cliente_id: ID del cliente
            
        Returns:
            Diccionario con información del cliente y sus proyectos
        """
        cliente = self.get_by_id(db=db, obj_id=cliente_id)
        
        if not cliente:
            return None
        
        proyectos = db.query(Proyecto).filter(
            and_(
                Proyecto.cliente_id == cliente_id,
                Proyecto.activo == True
            )
        ).all()
        
        return {
            "cliente": cliente,
            "proyectos": proyectos,
            "total_proyectos": len(proyectos)
        }
    
    def get_statistics(self, db: Session, *, cliente_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtener estadísticas de un cliente.
        
        Args:
            db: Sesión de base de datos
            cliente_id: ID del cliente
            
        Returns:
            Diccionario con estadísticas del cliente
        """
        cliente = self.get_by_id(db=db, obj_id=cliente_id)
        
        if not cliente:
            return None
        
        # Estadísticas de proyectos
        proyectos_stats = db.query(
            func.count(Proyecto.id).label("total_proyectos"),
            func.count().filter(Proyecto.estado == "completado").label("proyectos_completados"),
            func.count().filter(Proyecto.estado == "en_progreso").label("proyectos_en_progreso"),
            func.sum(Proyecto.presupuesto).label("presupuesto_total"),
            func.sum(Proyecto.costo_real).label("costo_real_total")
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
            func.sum(Cotizacion.total).label("valor_total_cotizaciones")
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
    
    def get_most_active(
        self,
        db: Session,
        *,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Obtener clientes más activos (con más proyectos).
        
        Args:
            db: Sesión de base de datos
            limit: Número máximo de clientes a devolver
            
        Returns:
            Lista de clientes más activos
        """
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
        ).limit(limit).all()
        
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
    
    def validate_unique_email(
        self,
        db: Session,
        *,
        email: str,
        exclude_id: Optional[int] = None
    ) -> bool:
        """
        Validar que el email sea único.
        
        Args:
            db: Sesión de base de datos
            email: Email a validar
            exclude_id: ID a excluir de la validación (para actualizaciones)
            
        Returns:
            True si el email es único, False en caso contrario
        """
        query = db.query(Cliente).filter(Cliente.email == email)
        
        if exclude_id:
            query = query.filter(Cliente.id != exclude_id)
        
        existing = query.first()
        return existing is None


# Instancia del servicio
cliente_service = ClienteService()
