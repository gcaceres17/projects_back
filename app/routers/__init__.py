from .auth import router as auth_router
from .colaboradores import router as colaboradores_router
from .proyectos import router as proyectos_router

__all__ = [
    "auth_router",
    "colaboradores_router", 
    "proyectos_router"
]
