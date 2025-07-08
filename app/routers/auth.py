from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.auth import authenticate_user, create_access_token, get_current_active_user, get_password_hash
from app.models import Usuario
from app.schemas.usuario import UsuarioLogin, Token, UsuarioCreate, UsuarioResponse, CambiarPassword
from app.config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()


@router.post("/login", response_model=Token)
async def login_for_access_token(
    user_credentials: UsuarioLogin,
    db: Session = Depends(get_db)
):
    """
    Autenticar usuario y obtener token de acceso.
    
    Args:
        user_credentials: Email y contraseña del usuario
        db: Sesión de base de datos
        
    Returns:
        Token: Token de acceso JWT
        
    Raises:
        HTTPException: Si las credenciales son incorrectas
    """
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario inactivo",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    logger.info(f"Usuario {user.email} inició sesión")
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/register", response_model=UsuarioResponse)
async def register_user(
    user: UsuarioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Registrar un nuevo usuario.
    
    Requiere autenticación de usuario activo.
    Solo administradores pueden crear usuarios.
    
    Args:
        user: Datos del usuario a crear
        db: Sesión de base de datos
        current_user: Usuario actual autenticado
        
    Returns:
        UsuarioResponse: Datos del usuario creado
        
    Raises:
        HTTPException: Si el usuario no es admin o el email ya existe
    """
    # Verificar permisos de administrador
    if not current_user.es_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para crear usuarios"
        )
    
    # Verificar si el email ya existe
    existing_user = db.query(Usuario).filter(Usuario.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con este email"
        )
    
    # Crear nuevo usuario
    hashed_password = get_password_hash(user.password)
    db_user = Usuario(
        email=user.email,
        nombre=user.nombre,
        apellido=user.apellido,
        hashed_password=hashed_password,
        es_admin=user.es_admin,
        activo=user.activo
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    logger.info(f"Usuario {db_user.email} registrado por {current_user.email}")
    
    return db_user


@router.get("/me", response_model=UsuarioResponse)
async def read_users_me(
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtener información del usuario actual.
    
    Args:
        current_user: Usuario actual autenticado
        
    Returns:
        UsuarioResponse: Información del usuario actual
    """
    return current_user


@router.post("/change-password")
async def change_password(
    password_data: CambiarPassword,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Cambiar contraseña del usuario actual.
    
    Args:
        password_data: Contraseña actual y nueva contraseña
        db: Sesión de base de datos
        current_user: Usuario actual autenticado
        
    Returns:
        dict: Mensaje de confirmación
        
    Raises:
        HTTPException: Si la contraseña actual es incorrecta
    """
    # Verificar contraseña actual
    if not authenticate_user(db, current_user.email, password_data.password_actual):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contraseña actual incorrecta"
        )
    
    # Actualizar contraseña
    current_user.hashed_password = get_password_hash(password_data.password_nueva)
    db.commit()
    
    logger.info(f"Usuario {current_user.email} cambió su contraseña")
    
    return {"message": "Contraseña cambiada exitosamente"}


@router.post("/logout")
async def logout(
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Cerrar sesión (logout).
    
    Nota: Con JWT, el logout se maneja en el frontend eliminando el token.
    Este endpoint es principalmente para logging.
    
    Args:
        current_user: Usuario actual autenticado
        
    Returns:
        dict: Mensaje de confirmación
    """
    logger.info(f"Usuario {current_user.email} cerró sesión")
    
    return {"message": "Sesión cerrada exitosamente"}


@router.get("/verify-token")
async def verify_token(
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Verificar si el token actual es válido.
    
    Args:
        current_user: Usuario actual autenticado
        
    Returns:
        dict: Estado del token y usuario
    """
    return {
        "valid": True,
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "nombre": current_user.nombre,
            "apellido": current_user.apellido,
            "es_admin": current_user.es_admin
        }
    }
