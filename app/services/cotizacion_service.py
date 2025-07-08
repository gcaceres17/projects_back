"""
Servicio para gestión de cotizaciones.

Este módulo contiene la lógica de negocio específica para cotizaciones.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, extract
from datetime import datetime

from app.models import Cotizacion, Cliente, Proyecto
from app.schemas.cotizacion import CotizacionCreate, CotizacionUpdate
from app.services.base_service import BaseService


class CotizacionService(BaseService[Cotizacion, CotizacionCreate, CotizacionUpdate]):
    """
    Servicio para operaciones específicas de cotizaciones.
    """
    
    def __init__(self):
        super().__init__(Cotizacion)
    
    def get_by_estado(
        self,
        db: Session,
        *,
        estado: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Cotizacion]:
        """
        Obtener cotizaciones por estado.
        
        Args:
            db: Sesión de base de datos
            estado: Estado de la cotización
            skip: Número de registros a omitir
            limit: Número máximo de registros a devolver
            
        Returns:
            Lista de cotizaciones
        """
        return db.query(Cotizacion).filter(
            Cotizacion.estado == estado
        ).offset(skip).limit(limit).all()
    
    def get_by_cliente(
        self,
        db: Session,
        *,
        cliente_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Cotizacion]:
        """
        Obtener cotizaciones por cliente.
        
        Args:
            db: Sesión de base de datos
            cliente_id: ID del cliente
            skip: Número de registros a omitir
            limit: Número máximo de registros a devolver
            
        Returns:
            Lista de cotizaciones del cliente
        """
        return db.query(Cotizacion).filter(
            and_(
                Cotizacion.cliente_id == cliente_id,
                Cotizacion.activo == True
            )
        ).offset(skip).limit(limit).all()
    
    def get_by_proyecto(
        self,
        db: Session,
        *,
        proyecto_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Cotizacion]:
        """
        Obtener cotizaciones por proyecto.
        
        Args:
            db: Sesión de base de datos
            proyecto_id: ID del proyecto
            skip: Número de registros a omitir
            limit: Número máximo de registros a devolver
            
        Returns:
            Lista de cotizaciones del proyecto
        """
        return db.query(Cotizacion).filter(
            and_(
                Cotizacion.proyecto_id == proyecto_id,
                Cotizacion.activo == True
            )
        ).offset(skip).limit(limit).all()
    
    def get_by_date_range(
        self,
        db: Session,
        *,
        fecha_inicio: datetime,
        fecha_fin: datetime,
        skip: int = 0,
        limit: int = 100
    ) -> List[Cotizacion]:
        """
        Obtener cotizaciones en un rango de fechas.
        
        Args:
            db: Sesión de base de datos
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            skip: Número de registros a omitir
            limit: Número máximo de registros a devolver
            
        Returns:
            Lista de cotizaciones en el rango
        """
        return db.query(Cotizacion).filter(
            and_(
                Cotizacion.fecha_creacion >= fecha_inicio,
                Cotizacion.fecha_creacion <= fecha_fin,
                Cotizacion.activo == True
            )
        ).offset(skip).limit(limit).all()
    
    def get_with_details(self, db: Session, *, cotizacion_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtener cotización con detalles completos.
        
        Args:
            db: Sesión de base de datos
            cotizacion_id: ID de la cotización
            
        Returns:
            Diccionario con información detallada de la cotización
        """
        cotizacion = db.query(Cotizacion).filter(
            Cotizacion.id == cotizacion_id
        ).first()
        
        if not cotizacion:
            return None
        
        # Obtener cliente
        cliente = db.query(Cliente).filter(
            Cliente.id == cotizacion.cliente_id
        ).first()
        
        # Obtener proyecto si existe
        proyecto = None
        if cotizacion.proyecto_id:
            proyecto = db.query(Proyecto).filter(
                Proyecto.id == cotizacion.proyecto_id
            ).first()
        
        return {
            "cotizacion": cotizacion,
            "cliente": cliente,
            "proyecto": proyecto
        }
    
    def get_statistics(self, db: Session) -> Dict[str, Any]:
        """
        Obtener estadísticas generales de cotizaciones.
        
        Args:
            db: Sesión de base de datos
            
        Returns:
            Diccionario con estadísticas
        """
        # Estadísticas generales
        total_cotizaciones = db.query(func.count(Cotizacion.id)).scalar()
        
        cotizaciones_por_estado = db.query(
            Cotizacion.estado,
            func.count(Cotizacion.id).label('cantidad')
        ).group_by(Cotizacion.estado).all()
        
        # Valor total
        valor_total = db.query(func.sum(Cotizacion.total)).scalar() or 0
        
        # Valor por estado
        valor_por_estado = db.query(
            Cotizacion.estado,
            func.sum(Cotizacion.total).label('valor_total')
        ).group_by(Cotizacion.estado).all()
        
        return {
            "total_cotizaciones": total_cotizaciones,
            "valor_total": float(valor_total),
            "por_estado": [
                {
                    "estado": estado,
                    "cantidad": cantidad
                }
                for estado, cantidad in cotizaciones_por_estado
            ],
            "valor_por_estado": [
                {
                    "estado": estado,
                    "valor_total": float(valor_total)
                }
                for estado, valor_total in valor_por_estado
            ]
        }
    
    def get_monthly_stats(self, db: Session, *, año: int) -> List[Dict[str, Any]]:
        """
        Obtener estadísticas mensuales de cotizaciones.
        
        Args:
            db: Sesión de base de datos
            año: Año para las estadísticas
            
        Returns:
            Lista con estadísticas por mes
        """
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
    
    def aprobar_cotizacion(self, db: Session, *, cotizacion_id: int) -> Optional[Cotizacion]:
        """
        Aprobar una cotización.
        
        Args:
            db: Sesión de base de datos
            cotizacion_id: ID de la cotización
            
        Returns:
            Cotización aprobada o None si no existe
        """
        cotizacion = self.get_by_id(db=db, obj_id=cotizacion_id)
        
        if not cotizacion:
            return None
        
        cotizacion.estado = "aprobada"
        cotizacion.fecha_aprobacion = datetime.now()
        
        db.commit()
        db.refresh(cotizacion)
        
        return cotizacion
    
    def rechazar_cotizacion(
        self,
        db: Session,
        *,
        cotizacion_id: int,
        motivo: Optional[str] = None
    ) -> Optional[Cotizacion]:
        """
        Rechazar una cotización.
        
        Args:
            db: Sesión de base de datos
            cotizacion_id: ID de la cotización
            motivo: Motivo del rechazo
            
        Returns:
            Cotización rechazada o None si no existe
        """
        cotizacion = self.get_by_id(db=db, obj_id=cotizacion_id)
        
        if not cotizacion:
            return None
        
        cotizacion.estado = "rechazada"
        if motivo:
            cotizacion.observaciones = motivo
        
        db.commit()
        db.refresh(cotizacion)
        
        return cotizacion
    
    def calcular_total(self, items: List[Dict[str, Any]]) -> float:
        """
        Calcular el total de una cotización basado en sus items.
        
        Args:
            items: Lista de items de la cotización
            
        Returns:
            Total calculado
        """
        total = 0.0
        
        for item in items:
            cantidad = item.get('cantidad', 0)
            precio_unitario = item.get('precio_unitario', 0)
            total += cantidad * precio_unitario
        
        return total


# Instancia del servicio
cotizacion_service = CotizacionService()
