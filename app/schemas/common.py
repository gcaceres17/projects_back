from pydantic import BaseModel
from typing import Generic, TypeVar, List, Optional

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    """Esquema para respuestas paginadas."""
    items: List[T]
    total: int
    page: int = 1
    size: int = 10
    pages: int
    
    @classmethod
    def create(cls, items: List[T], total: int, page: int = 1, size: int = 10):
        """Crear respuesta paginada."""
        pages = (total + size - 1) // size  # Calcular número de páginas
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages
        )
