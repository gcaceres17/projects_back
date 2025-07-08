#!/bin/bash
set -e

# Script de inicialización de PostgreSQL
echo "🚀 Iniciando configuración de base de datos..."

# Crear usuario adicional si no existe
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Crear usuario de aplicación si no existe
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'app_user') THEN
            CREATE USER app_user WITH PASSWORD 'app_password';
            GRANT CONNECT ON DATABASE proyecto_db TO app_user;
            GRANT USAGE ON SCHEMA public TO app_user;
            GRANT CREATE ON SCHEMA public TO app_user;
            ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO app_user;
            ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO app_user;
        END IF;
    END
    \$\$;

    -- Crear extensiones útiles
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pg_trgm";
    CREATE EXTENSION IF NOT EXISTS "unaccent";

    -- Configurar timezone
    SET timezone = 'America/Bogota';

    -- Crear esquema para auditoría (opcional)
    CREATE SCHEMA IF NOT EXISTS audit;
    GRANT USAGE ON SCHEMA audit TO app_user;
    GRANT CREATE ON SCHEMA audit TO app_user;

EOSQL

echo "✅ Base de datos configurada exitosamente"
echo "📊 Información de la base de datos:"
echo "   - Base de datos: $POSTGRES_DB"
echo "   - Usuario principal: $POSTGRES_USER"
echo "   - Usuario de aplicación: app_user"
echo "   - Extensiones instaladas: uuid-ossp, pg_trgm, unaccent"
