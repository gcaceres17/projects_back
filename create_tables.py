#!/usr/bin/env python3
"""
Script para crear tablas de la base de datos directamente
sin usar Alembic, para evitar problemas de codificación.
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Cargar variables de entorno
load_dotenv()

# Configurar la conexión a la base de datos
DATABASE_URL = os.getenv("DATABASE_URL")

def create_database_tables():
    """Crear todas las tablas necesarias"""
    try:
        # Crear el motor de la base de datos
        engine = create_engine(DATABASE_URL)
        
        # Probar la conexión
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()
            print(f"✅ Conexión exitosa a PostgreSQL: {version[0]}")
        
        # Crear las tablas
        sql_commands = [
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                nombre VARCHAR(100) NOT NULL,
                apellido VARCHAR(100) NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                rol VARCHAR(50) DEFAULT 'usuario' NOT NULL,
                activo BOOLEAN DEFAULT true NOT NULL,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS clientes (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(200) NOT NULL,
                email VARCHAR(255),
                telefono VARCHAR(20),
                direccion TEXT,
                ciudad VARCHAR(100),
                pais VARCHAR(100) DEFAULT 'Colombia',
                tipo_cliente VARCHAR(50) DEFAULT 'empresa',
                activo BOOLEAN DEFAULT true NOT NULL,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS colaboradores (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                apellido VARCHAR(100) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                telefono VARCHAR(20),
                tipo_colaborador VARCHAR(50) DEFAULT 'interno',
                departamento VARCHAR(100),
                cargo VARCHAR(100),
                habilidades TEXT[],
                costo_hora DECIMAL(10,2),
                disponible BOOLEAN DEFAULT true NOT NULL,
                activo BOOLEAN DEFAULT true NOT NULL,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS proyectos (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(200) NOT NULL,
                descripcion TEXT,
                cliente_id INTEGER REFERENCES clientes(id),
                estado VARCHAR(50) DEFAULT 'planificacion',
                prioridad VARCHAR(50) DEFAULT 'media',
                fecha_inicio DATE,
                fecha_fin_estimada DATE,
                fecha_fin_real DATE,
                presupuesto DECIMAL(12,2),
                costo_real DECIMAL(12,2) DEFAULT 0,
                horas_estimadas INTEGER,
                horas_reales INTEGER DEFAULT 0,
                progreso INTEGER DEFAULT 0,
                activo BOOLEAN DEFAULT true NOT NULL,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS proyecto_colaboradores (
                id SERIAL PRIMARY KEY,
                proyecto_id INTEGER REFERENCES proyectos(id),
                colaborador_id INTEGER REFERENCES colaboradores(id),
                rol VARCHAR(100),
                fecha_asignacion DATE DEFAULT CURRENT_DATE,
                fecha_desasignacion DATE,
                activo BOOLEAN DEFAULT true NOT NULL,
                UNIQUE(proyecto_id, colaborador_id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS cotizaciones (
                id SERIAL PRIMARY KEY,
                numero VARCHAR(50) UNIQUE NOT NULL,
                cliente_id INTEGER REFERENCES clientes(id),
                proyecto_id INTEGER REFERENCES proyectos(id),
                estado VARCHAR(50) DEFAULT 'borrador',
                fecha_cotizacion DATE DEFAULT CURRENT_DATE,
                fecha_vencimiento DATE,
                subtotal DECIMAL(12,2) DEFAULT 0,
                descuento DECIMAL(12,2) DEFAULT 0,
                impuestos DECIMAL(12,2) DEFAULT 0,
                total DECIMAL(12,2) DEFAULT 0,
                observaciones TEXT,
                activo BOOLEAN DEFAULT true NOT NULL,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS cotizacion_items (
                id SERIAL PRIMARY KEY,
                cotizacion_id INTEGER REFERENCES cotizaciones(id),
                descripcion TEXT NOT NULL,
                cantidad DECIMAL(10,2) NOT NULL,
                precio_unitario DECIMAL(10,2) NOT NULL,
                subtotal DECIMAL(12,2) NOT NULL,
                orden INTEGER DEFAULT 0
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS costos_rigidos (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(200) NOT NULL,
                descripcion TEXT,
                categoria VARCHAR(100) NOT NULL,
                tipo VARCHAR(50) DEFAULT 'fijo',
                monto DECIMAL(10,2) NOT NULL,
                frecuencia VARCHAR(50) DEFAULT 'mensual',
                proveedor VARCHAR(200),
                proyecto_id INTEGER REFERENCES proyectos(id),
                fecha_inicio DATE NOT NULL,
                fecha_fin DATE,
                activo BOOLEAN DEFAULT true NOT NULL,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
            CREATE INDEX IF NOT EXISTS idx_usuarios_activo ON usuarios(activo);
            CREATE INDEX IF NOT EXISTS idx_clientes_nombre ON clientes(nombre);
            CREATE INDEX IF NOT EXISTS idx_clientes_activo ON clientes(activo);
            CREATE INDEX IF NOT EXISTS idx_colaboradores_email ON colaboradores(email);
            CREATE INDEX IF NOT EXISTS idx_colaboradores_activo ON colaboradores(activo);
            CREATE INDEX IF NOT EXISTS idx_proyectos_cliente_id ON proyectos(cliente_id);
            CREATE INDEX IF NOT EXISTS idx_proyectos_estado ON proyectos(estado);
            CREATE INDEX IF NOT EXISTS idx_proyectos_activo ON proyectos(activo);
            CREATE INDEX IF NOT EXISTS idx_cotizaciones_cliente_id ON cotizaciones(cliente_id);
            CREATE INDEX IF NOT EXISTS idx_cotizaciones_estado ON cotizaciones(estado);
            CREATE INDEX IF NOT EXISTS idx_cotizaciones_numero ON cotizaciones(numero);
            CREATE INDEX IF NOT EXISTS idx_costos_rigidos_proyecto_id ON costos_rigidos(proyecto_id);
            CREATE INDEX IF NOT EXISTS idx_costos_rigidos_categoria ON costos_rigidos(categoria);
            """
        ]
        
        with engine.connect() as conn:
            for sql_command in sql_commands:
                if sql_command.strip():
                    conn.execute(text(sql_command))
                    conn.commit()
        
        print("✅ Todas las tablas han sido creadas exitosamente")
        
    except Exception as e:
        print(f"❌ Error al crear las tablas: {e}")
        raise

if __name__ == "__main__":
    create_database_tables()
