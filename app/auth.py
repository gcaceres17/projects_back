from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models import Usuario
from app.schemas.usuario import TokenData
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# Configurar el contexto de hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configurar el esquema de autenticación
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verificar si una contraseña en texto plano coincide con la hasheada.
    
    Args:
        plain_password: Contraseña en texto plano
        hashed_password: Contraseña hasheada
        
    Returns:
        bool: True si coinciden, False si no
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Generar hash de contraseña.
    
    Args:
        password: Contraseña en texto plano
        
    Returns:
        str: Contraseña hasheada
    """
    return pwd_context.hash(password)


def authenticate_user(db: Session, email: str, password: str) -> Union[Usuario, bool]:
    """
    Autenticar un usuario.
    
    Args:
        db: Sesión de base de datos
        email: Email del usuario
        password: Contraseña del usuario
        
    Returns:
        Usuario: El usuario si la autenticación es exitosa
        bool: False si la autenticación falla
    """
    user = db.query(Usuario).filter(Usuario.email == email).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crear un token de acceso JWT.
    
    Args:
        data: Datos a incluir en el token
        expires_delta: Tiempo de expiración del token
        
    Returns:
        str: Token JWT codificado
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Usuario:
    """
    Obtener el usuario actual a partir del token JWT.
    
    Args:
        credentials: Credenciales de autorización
        db: Sesión de base de datos
        
    Returns:
        Usuario: El usuario actual
        
    Raises:
        HTTPException: Si el token es inválido o el usuario no existe
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = db.query(Usuario).filter(Usuario.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    
    # Actualizar fecha de último acceso
    user.fecha_ultimo_acceso = datetime.utcnow()
    db.commit()
    
    return user


async def get_current_active_user(
    current_user: Usuario = Depends(get_current_user)
) -> Usuario:
    """
    Obtener el usuario actual y verificar que esté activo.
    
    Args:
        current_user: Usuario actual
        
    Returns:
        Usuario: El usuario actual si está activo
        
    Raises:
        HTTPException: Si el usuario está inactivo
    """
    if not current_user.activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    return current_user


async def get_current_admin_user(
    current_user: Usuario = Depends(get_current_active_user)
) -> Usuario:
    """
    Obtener el usuario actual y verificar que sea administrador.
    
    Args:
        current_user: Usuario actual
        
    Returns:
        Usuario: El usuario actual si es administrador
        
    Raises:
        HTTPException: Si el usuario no es administrador
    """
    if not current_user.es_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos suficientes para realizar esta acción"
        )
    return current_user


def generate_username_from_email(email: str) -> str:
    """
    Generar un nombre de usuario a partir del email.
    
    Args:
        email: Email del usuario
        
    Returns:
        str: Nombre de usuario generado
    """
    return email.split("@")[0]


def is_valid_password(password: str) -> tuple[bool, str]:
    """
    Validar que una contraseña cumpla con los requisitos de seguridad.
    
    Args:
        password: Contraseña a validar
        
    Returns:
        tuple: (es_válida, mensaje_error)
    """
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"
    
    if not any(c.isupper() for c in password):
        return False, "La contraseña debe tener al menos una mayúscula"
    
    if not any(c.islower() for c in password):
        return False, "La contraseña debe tener al menos una minúscula"
    
    if not any(c.isdigit() for c in password):
        return False, "La contraseña debe tener al menos un número"
    
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        return False, "La contraseña debe tener al menos un carácter especial"
    
    return True, "Contraseña válida"


def create_first_admin_user(db: Session) -> Usuario:
    """
    Crear el primer usuario administrador del sistema.
    
    Args:
        db: Sesión de base de datos
        
    Returns:
        Usuario: El usuario administrador creado
    """
    admin_email = "admin@sistema.com"
    admin_password = "Admin123!"
    
    # Verificar si ya existe un usuario admin
    existing_admin = db.query(Usuario).filter(Usuario.email == admin_email).first()
    if existing_admin:
        return existing_admin
    
    # Crear el usuario administrador
    admin_user = Usuario(
        email=admin_email,
        nombre="Administrador",
        apellido="Sistema",
        hashed_password=get_password_hash(admin_password),
        es_admin=True,
        activo=True
    )
    
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    logger.info(f"Usuario administrador creado: {admin_email}")
    return admin_user
