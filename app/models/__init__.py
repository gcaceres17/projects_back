from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Table, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class EstadoProyecto(enum.Enum):
    """Estados posibles de un proyecto."""
    PLANIFICACION = "planificacion"
    EN_PROGRESO = "en_progreso"
    PAUSADO = "pausado"
    COMPLETADO = "completado"
    CANCELADO = "cancelado"


class EstadoCotizacion(enum.Enum):
    """Estados posibles de una cotización."""
    BORRADOR = "borrador"
    ENVIADA = "enviada"
    APROBADA = "aprobada"
    RECHAZADA = "rechazada"
    VENCIDA = "vencida"


class TipoColaborador(enum.Enum):
    """Tipos de colaborador."""
    INTERNO = "interno"
    EXTERNO = "externo"
    FREELANCE = "freelance"


class TipoCosto(enum.Enum):
    """Tipos de costo rígido."""
    FIJO = "fijo"
    VARIABLE = "variable"
    RECURRENTE = "recurrente"


# Tabla de asociación muchos-a-muchos entre proyectos y colaboradores
proyecto_colaborador = Table(
    'proyecto_colaborador',
    Base.metadata,
    Column('proyecto_id', Integer, ForeignKey('proyectos.id'), primary_key=True),
    Column('colaborador_id', Integer, ForeignKey('colaboradores.id'), primary_key=True),
    Column('horas_asignadas', Float, default=0.0),
    Column('fecha_asignacion', DateTime, default=func.now()),
    Column('activo', Boolean, default=True)
)


class Colaborador(Base):
    """
    Modelo para colaboradores del sistema.
    
    Representa a los empleados, contratistas y freelancers
    que pueden ser asignados a proyectos.
    """
    __tablename__ = "colaboradores"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, index=True)
    apellido = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    telefono = Column(String(20))
    cargo = Column(String(100), nullable=False)
    departamento = Column(String(100))
    tipo = Column(SQLEnum(TipoColaborador), nullable=False, default=TipoColaborador.INTERNO)
    costo_hora = Column(Float, nullable=False, default=0.0)
    disponible = Column(Boolean, default=True)
    habilidades = Column(Text)  # JSON string con habilidades
    fecha_ingreso = Column(DateTime, default=func.now())
    fecha_creacion = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())
    activo = Column(Boolean, default=True)
    
    # Relaciones
    proyectos = relationship("Proyecto", secondary=proyecto_colaborador, back_populates="colaboradores")
    
    def __repr__(self):
        return f"<Colaborador(id={self.id}, nombre='{self.nombre} {self.apellido}', email='{self.email}')>"


class Cliente(Base):
    """
    Modelo para clientes del sistema.
    
    Representa a las empresas o personas que contratan proyectos.
    """
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    telefono = Column(String(20))
    direccion = Column(Text)
    ciudad = Column(String(100))
    pais = Column(String(100))
    contacto_principal = Column(String(200))
    nit_ruc = Column(String(50), unique=True)
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relaciones
    proyectos = relationship("Proyecto", back_populates="cliente")
    cotizaciones = relationship("Cotizacion", back_populates="cliente")
    
    def __repr__(self):
        return f"<Cliente(id={self.id}, nombre='{self.nombre}', email='{self.email}')>"


class Proyecto(Base):
    """
    Modelo para proyectos del sistema.
    
    Representa los proyectos que se desarrollan para los clientes.
    """
    __tablename__ = "proyectos"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False, index=True)
    descripcion = Column(Text)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    estado = Column(SQLEnum(EstadoProyecto), nullable=False, default=EstadoProyecto.PLANIFICACION)
    fecha_inicio = Column(DateTime)
    fecha_fin_estimada = Column(DateTime)
    fecha_fin_real = Column(DateTime)
    presupuesto = Column(Float, nullable=False, default=0.0)
    costo_real = Column(Float, default=0.0)
    horas_estimadas = Column(Float, default=0.0)
    horas_trabajadas = Column(Float, default=0.0)
    progreso = Column(Float, default=0.0)  # Porcentaje de 0 a 100
    prioridad = Column(Integer, default=1)  # 1=Alta, 2=Media, 3=Baja
    notas = Column(Text)
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relaciones
    cliente = relationship("Cliente", back_populates="proyectos")
    colaboradores = relationship("Colaborador", secondary=proyecto_colaborador, back_populates="proyectos")
    cotizaciones = relationship("Cotizacion", back_populates="proyecto")
    costos_rigidos = relationship("CostoRigido", back_populates="proyecto")
    
    def __repr__(self):
        return f"<Proyecto(id={self.id}, nombre='{self.nombre}', estado='{self.estado}')>"


class Cotizacion(Base):
    """
    Modelo para cotizaciones del sistema.
    
    Representa las cotizaciones enviadas a los clientes.
    """
    __tablename__ = "cotizaciones"
    
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(50), unique=True, nullable=False, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    proyecto_id = Column(Integer, ForeignKey("proyectos.id"))
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text)
    subtotal = Column(Float, nullable=False, default=0.0)
    impuestos = Column(Float, default=0.0)
    descuento = Column(Float, default=0.0)
    total = Column(Float, nullable=False, default=0.0)
    estado = Column(SQLEnum(EstadoCotizacion), nullable=False, default=EstadoCotizacion.BORRADOR)
    fecha_creacion = Column(DateTime, default=func.now())
    fecha_envio = Column(DateTime)
    fecha_vencimiento = Column(DateTime)
    fecha_aprobacion = Column(DateTime)
    validez_dias = Column(Integer, default=30)
    terminos_condiciones = Column(Text)
    notas = Column(Text)
    activo = Column(Boolean, default=True)
    
    # Relaciones
    cliente = relationship("Cliente", back_populates="cotizaciones")
    proyecto = relationship("Proyecto", back_populates="cotizaciones")
    items = relationship("ItemCotizacion", back_populates="cotizacion", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Cotizacion(id={self.id}, numero='{self.numero}', total={self.total})>"


class ItemCotizacion(Base):
    """
    Modelo para items de cotización.
    
    Representa los elementos individuales de una cotización.
    """
    __tablename__ = "items_cotizacion"
    
    id = Column(Integer, primary_key=True, index=True)
    cotizacion_id = Column(Integer, ForeignKey("cotizaciones.id"), nullable=False)
    descripcion = Column(String(500), nullable=False)
    cantidad = Column(Float, nullable=False, default=1.0)
    precio_unitario = Column(Float, nullable=False, default=0.0)
    subtotal = Column(Float, nullable=False, default=0.0)
    orden = Column(Integer, default=1)
    activo = Column(Boolean, default=True)
    
    # Relaciones
    cotizacion = relationship("Cotizacion", back_populates="items")
    
    def __repr__(self):
        return f"<ItemCotizacion(id={self.id}, descripcion='{self.descripcion}', subtotal={self.subtotal})>"


class CostoRigido(Base):
    """
    Modelo para costos rígidos del sistema.
    
    Representa los costos fijos y variables que se aplican a los proyectos.
    """
    __tablename__ = "costos_rigidos"
    
    id = Column(Integer, primary_key=True, index=True)
    proyecto_id = Column(Integer, ForeignKey("proyectos.id"))
    nombre = Column(String(200), nullable=False, index=True)
    descripcion = Column(Text)
    tipo = Column(SQLEnum(TipoCosto), nullable=False, default=TipoCosto.FIJO)
    valor = Column(Float, nullable=False, default=0.0)
    moneda = Column(String(10), default="USD")
    frecuencia = Column(String(50))  # mensual, anual, único, etc.
    fecha_aplicacion = Column(DateTime, default=func.now())
    categoria = Column(String(100))  # infraestructura, software, recursos, etc.
    proveedor = Column(String(200))
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relaciones
    proyecto = relationship("Proyecto", back_populates="costos_rigidos")
    
    def __repr__(self):
        return f"<CostoRigido(id={self.id}, nombre='{self.nombre}', valor={self.valor})>"


class Usuario(Base):
    """
    Modelo para usuarios del sistema.
    
    Representa a los usuarios que pueden acceder al sistema.
    """
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    es_admin = Column(Boolean, default=False)
    activo = Column(Boolean, default=True)
    fecha_ultimo_acceso = Column(DateTime)
    fecha_creacion = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Usuario(id={self.id}, email='{self.email}', nombre='{self.nombre}')>"
