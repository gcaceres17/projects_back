"""
Servicio para gestión de costos rígidos.

Este módulo contiene la lógica de negocio específica para costos rígidos.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, extract
from datetime import datetime, timedelta

from app.models import CostoRigido
from app.schemas.costo_rigido import CostoRigidoCreate, CostoRigidoUpdate
from app.services.base_service import BaseService


class CostoRigidoService(BaseService[CostoRigido, CostoRigidoCreate, CostoRigidoUpdate]):
    """
    Servicio para operaciones específicas de costos rígidos.
    """
    
    def __init__(self):
        super().__init__(CostoRigido)
    
    def get_by_categoria(
        self,
        db: Session,
        *,
        categoria: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[CostoRigido]:
        """
        Obtener costos rígidos por categoría.
        
        Args:
            db: Sesión de base de datos
            categoria: Categoría del costo
            skip: Número de registros a omitir
            limit: Número máximo de registros a devolver
            
        Returns:
            Lista de costos rígidos
        """
        return db.query(CostoRigido).filter(
            CostoRigido.categoria == categoria
        ).offset(skip).limit(limit).all()
    
    def get_by_frecuencia(
        self,
        db: Session,
        *,
        frecuencia: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[CostoRigido]:
        """
        Obtener costos rígidos por frecuencia.
        
        Args:
            db: Sesión de base de datos
            frecuencia: Frecuencia del costo
            skip: Número de registros a omitir
            limit: Número máximo de registros a devolver
            
        Returns:
            Lista de costos rígidos
        """
        return db.query(CostoRigido).filter(
            CostoRigido.frecuencia == frecuencia
        ).offset(skip).limit(limit).all()
    
    def get_by_proveedor(
        self,
        db: Session,
        *,
        proveedor: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[CostoRigido]:
        """
        Obtener costos rígidos por proveedor.
        
        Args:
            db: Sesión de base de datos
            proveedor: Proveedor del costo
            skip: Número de registros a omitir
            limit: Número máximo de registros a devolver
            
        Returns:
            Lista de costos rígidos
        """
        return db.query(CostoRigido).filter(
            CostoRigido.proveedor.ilike(f"%{proveedor}%")
        ).offset(skip).limit(limit).all()
    
    def get_by_date_range(
        self,
        db: Session,
        *,
        fecha_inicio: datetime,
        fecha_fin: datetime,
        skip: int = 0,
        limit: int = 100
    ) -> List[CostoRigido]:
        """
        Obtener costos rígidos en un rango de fechas.
        
        Args:
            db: Sesión de base de datos
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            skip: Número de registros a omitir
            limit: Número máximo de registros a devolver
            
        Returns:
            Lista de costos rígidos en el rango
        """
        return db.query(CostoRigido).filter(
            and_(
                CostoRigido.fecha_aplicacion >= fecha_inicio,
                CostoRigido.fecha_aplicacion <= fecha_fin,
                CostoRigido.activo == True
            )
        ).offset(skip).limit(limit).all()
    
    def get_activos(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[CostoRigido]:
        """
        Obtener costos rígidos activos.
        
        Args:
            db: Sesión de base de datos
            skip: Número de registros a omitir
            limit: Número máximo de registros a devolver
            
        Returns:
            Lista de costos rígidos activos
        """
        return db.query(CostoRigido).filter(
            CostoRigido.activo == True
        ).offset(skip).limit(limit).all()
    
    def get_statistics(self, db: Session) -> Dict[str, Any]:
        """
        Obtener estadísticas generales de costos rígidos.
        
        Args:
            db: Sesión de base de datos
            
        Returns:
            Diccionario con estadísticas
        """
        # Total de costos rígidos
        total_costos = db.query(func.count(CostoRigido.id)).scalar()
        
        # Total de monto
        total_monto = db.query(func.sum(CostoRigido.monto)).scalar() or 0
        
        # Costos por categoría
        costos_por_categoria = db.query(
            CostoRigido.categoria,
            func.count(CostoRigido.id).label('cantidad'),
            func.sum(CostoRigido.monto).label('total')
        ).group_by(CostoRigido.categoria).all()
        
        # Costos por frecuencia
        costos_por_frecuencia = db.query(
            CostoRigido.frecuencia,
            func.count(CostoRigido.id).label('cantidad'),
            func.sum(CostoRigido.monto).label('total')
        ).group_by(CostoRigido.frecuencia).all()
        
        # Costos activos vs inactivos
        costos_activos = db.query(func.count(CostoRigido.id)).filter(
            CostoRigido.activo == True
        ).scalar()
        
        costos_inactivos = db.query(func.count(CostoRigido.id)).filter(
            CostoRigido.activo == False
        ).scalar()
        
        return {
            "total_costos": total_costos,
            "total_monto": float(total_monto),
            "costos_activos": costos_activos,
            "costos_inactivos": costos_inactivos,
            "por_categoria": [
                {
                    "categoria": categoria,
                    "cantidad": cantidad,
                    "total": float(total)
                }
                for categoria, cantidad, total in costos_por_categoria
            ],
            "por_frecuencia": [
                {
                    "frecuencia": frecuencia,
                    "cantidad": cantidad,
                    "total": float(total)
                }
                for frecuencia, cantidad, total in costos_por_frecuencia
            ]
        }
    
    def get_monthly_costs(self, db: Session, *, año: int) -> List[Dict[str, Any]]:
        """
        Obtener costos mensuales.
        
        Args:
            db: Sesión de base de datos
            año: Año para las estadísticas
            
        Returns:
            Lista con costos por mes
        """
        resultado = db.query(
            extract('month', CostoRigido.fecha_aplicacion).label('mes'),
            func.count(CostoRigido.id).label('cantidad'),
            func.sum(CostoRigido.monto).label('total')
        ).filter(
            extract('year', CostoRigido.fecha_aplicacion) == año
        ).group_by(
            extract('month', CostoRigido.fecha_aplicacion)
        ).order_by(
            extract('month', CostoRigido.fecha_aplicacion)
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
                "total": float(total or 0)
            }
            for mes, cantidad, total in resultado
        ]
    
    def get_by_provider_stats(self, db: Session) -> List[Dict[str, Any]]:
        """
        Obtener estadísticas por proveedor.
        
        Args:
            db: Sesión de base de datos
            
        Returns:
            Lista con estadísticas por proveedor
        """
        resultado = db.query(
            CostoRigido.proveedor,
            func.count(CostoRigido.id).label('cantidad'),
            func.sum(CostoRigido.monto).label('total')
        ).group_by(
            CostoRigido.proveedor
        ).order_by(
            func.sum(CostoRigido.monto).desc()
        ).all()
        
        return [
            {
                "proveedor": proveedor,
                "cantidad": cantidad,
                "total": float(total or 0)
            }
            for proveedor, cantidad, total in resultado
        ]
    
    def calculate_monthly_cost(self, db: Session, *, categoria: Optional[str] = None) -> float:
        """
        Calcular el costo mensual total o por categoría.
        
        Args:
            db: Sesión de base de datos
            categoria: Categoría específica (opcional)
            
        Returns:
            Costo mensual calculado
        """
        query = db.query(CostoRigido).filter(CostoRigido.activo == True)
        
        if categoria:
            query = query.filter(CostoRigido.categoria == categoria)
        
        costos = query.all()
        
        total_mensual = 0.0
        
        for costo in costos:
            if costo.frecuencia == "mensual":
                total_mensual += costo.monto
            elif costo.frecuencia == "anual":
                total_mensual += costo.monto / 12
            elif costo.frecuencia == "trimestral":
                total_mensual += costo.monto / 3
            elif costo.frecuencia == "semestral":
                total_mensual += costo.monto / 6
        
        return total_mensual
    
    def search_by_name(
        self,
        db: Session,
        *,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[CostoRigido]:
        """
        Buscar costos rígidos por nombre.
        
        Args:
            db: Sesión de base de datos
            search_term: Término de búsqueda
            skip: Número de registros a omitir
            limit: Número máximo de registros a devolver
            
        Returns:
            Lista de costos rígidos que coinciden con la búsqueda
        """
        return db.query(CostoRigido).filter(
            CostoRigido.nombre.ilike(f"%{search_term}%")
        ).offset(skip).limit(limit).all()
    
    def get_upcoming_renewals(
        self,
        db: Session,
        *,
        days_ahead: int = 30
    ) -> List[CostoRigido]:
        """
        Obtener costos rígidos que vencen próximamente.
        
        Args:
            db: Sesión de base de datos
            days_ahead: Días hacia adelante para buscar vencimientos
            
        Returns:
            Lista de costos rígidos que vencen pronto
        """
        fecha_limite = datetime.now() + timedelta(days=days_ahead)
        
        return db.query(CostoRigido).filter(
            and_(
                CostoRigido.fecha_fin <= fecha_limite,
                CostoRigido.fecha_fin >= datetime.now(),
                CostoRigido.activo == True
            )
        ).all()


# Instancia del servicio
costo_rigido_service = CostoRigidoService()
