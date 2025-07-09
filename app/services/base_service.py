"""
Servicio base para operaciones CRUD comunes.

Este módulo proporciona una clase base que implementa operaciones CRUD
estándar que pueden ser reutilizadas por otros servicios.
"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Clase base para servicios CRUD.
    
    Proporciona operaciones básicas de Create, Read, Update y Delete
    que pueden ser reutilizadas por servicios específicos.
    """
    
    def __init__(self, model: Type[ModelType]):
        """
        Inicializar el servicio base.
        
        Args:
            model: Clase del modelo SQLAlchemy
        """
        self.model = model
    
    def get_by_id(self, db: Session, *, obj_id: int) -> Optional[ModelType]:
        """
        Obtener un objeto por su ID.
        
        Args:
            db: Sesión de base de datos
            obj_id: ID del objeto
            
        Returns:
            Objeto encontrado o None si no existe
        """
        return db.query(self.model).filter(self.model.id == obj_id).first()
    
    def get_multi(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[List] = None
    ) -> List[ModelType]:
        """
        Obtener múltiples objetos con paginación y filtros.
        
        Args:
            db: Sesión de base de datos
            skip: Número de registros a omitir
            limit: Número máximo de registros a devolver
            filters: Lista de filtros SQLAlchemy
            
        Returns:
            Lista de objetos
        """
        query = db.query(self.model)
        
        if filters:
            query = query.filter(and_(*filters))
        
        return query.offset(skip).limit(limit).all()
    
    def get_count(self, db: Session, *, filters: Optional[List] = None) -> int:
        """
        Contar el número total de objetos con filtros.
        
        Args:
            db: Sesión de base de datos
            filters: Lista de filtros SQLAlchemy
            
        Returns:
            Número total de objetos
        """
        query = db.query(self.model)
        
        if filters:
            query = query.filter(and_(*filters))
        
        return query.count()
    
    def get_paginated(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[List] = None,
        order_by: Optional[List] = None
    ) -> Dict[str, Any]:
        """
        Obtener datos paginados con metadatos.
        
        Args:
            db: Sesión de base de datos
            skip: Número de registros a omitir
            limit: Número máximo de registros a devolver
            filters: Lista de filtros SQLAlchemy
            
        Returns:
            Diccionario con datos paginados y metadatos
        """
        # Obtener datos
        items = self.get_multi(db=db, skip=skip, limit=limit, filters=filters)
        
        # Aplicar ordenamiento si se especifica
        if order_by:
            query = db.query(self.model)
            if filters:
                query = query.filter(and_(*filters))
            for order_field in order_by:
                query = query.order_by(order_field)
            items = query.offset(skip).limit(limit).all()
        
        # Contar total
        total = self.get_count(db=db, filters=filters)
        
        # Calcular metadatos de paginación
        total_pages = (total + limit - 1) // limit
        current_page = (skip // limit) + 1
        has_next = current_page < total_pages
        has_previous = current_page > 1
        
        return {
            "items": items,
            "total": total,
            "page": current_page,
            "size": limit,
            "pages": total_pages,
            "has_next": has_next,
            "has_previous": has_previous
        }
    
    def create(self, db: Session, *, obj_data: Union[CreateSchemaType, Dict[str, Any]]) -> ModelType:
        """
        Crear un nuevo objeto.
        
        Args:
            db: Sesión de base de datos
            obj_data: Datos del objeto a crear
            
        Returns:
            Objeto creado
        """
        if isinstance(obj_data, dict):
            obj_in_data = obj_data
        else:
            obj_in_data = jsonable_encoder(obj_data)
        
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return db_obj
    
    def update(
        self,
        db: Session,
        *,
        obj_id: int,
        obj_data: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> Optional[ModelType]:
        """
        Actualizar un objeto existente.
        
        Args:
            db: Sesión de base de datos
            obj_id: ID del objeto a actualizar
            obj_data: Datos de actualización
            
        Returns:
            Objeto actualizado o None si no existe
        """
        db_obj = self.get_by_id(db=db, obj_id=obj_id)
        
        if not db_obj:
            return None
        
        if isinstance(obj_data, dict):
            update_data = obj_data
        else:
            update_data = obj_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.commit()
        db.refresh(db_obj)
        
        return db_obj
    
    def delete(self, db: Session, *, obj_id: int) -> Optional[ModelType]:
        """
        Eliminar un objeto (soft delete si tiene campo 'activo').
        
        Args:
            db: Sesión de base de datos
            obj_id: ID del objeto a eliminar
            
        Returns:
            Objeto eliminado o None si no existe
        """
        db_obj = self.get_by_id(db=db, obj_id=obj_id)
        
        if not db_obj:
            return None
        
        # Verificar si el modelo tiene campo 'activo' para soft delete
        if hasattr(db_obj, 'activo'):
            db_obj.activo = False
            db.commit()
            db.refresh(db_obj)
        else:
            # Hard delete si no tiene campo 'activo'
            db.delete(db_obj)
            db.commit()
        
        return db_obj
    
    def get_by_field(
        self,
        db: Session,
        *,
        field_name: str,
        field_value: Any
    ) -> Optional[ModelType]:
        """
        Obtener un objeto por un campo específico.
        
        Args:
            db: Sesión de base de datos
            field_name: Nombre del campo
            field_value: Valor del campo
            
        Returns:
            Objeto encontrado o None si no existe
        """
        return db.query(self.model).filter(
            getattr(self.model, field_name) == field_value
        ).first()
    
    def get_multi_by_field(
        self,
        db: Session,
        *,
        field_name: str,
        field_value: Any,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """
        Obtener múltiples objetos por un campo específico.
        
        Args:
            db: Sesión de base de datos
            field_name: Nombre del campo
            field_value: Valor del campo
            skip: Número de registros a omitir
            limit: Número máximo de registros a devolver
            
        Returns:
            Lista de objetos
        """
        return db.query(self.model).filter(
            getattr(self.model, field_name) == field_value
        ).offset(skip).limit(limit).all()
    
    def exists(self, db: Session, *, obj_id: int) -> bool:
        """
        Verificar si existe un objeto con el ID dado.
        
        Args:
            db: Sesión de base de datos
            obj_id: ID del objeto
            
        Returns:
            True si existe, False en caso contrario
        """
        return db.query(self.model).filter(self.model.id == obj_id).first() is not None
    
    def get_active(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """
        Obtener objetos activos (si el modelo tiene campo 'activo').
        
        Args:
            db: Sesión de base de datos
            skip: Número de registros a omitir
            limit: Número máximo de registros a devolver
            
        Returns:
            Lista de objetos activos
        """
        query = db.query(self.model)
        
        if hasattr(self.model, 'activo'):
            query = query.filter(self.model.activo == True)
        
        return query.offset(skip).limit(limit).all()
