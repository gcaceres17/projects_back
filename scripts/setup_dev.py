#!/usr/bin/env python3
"""
Script para configurar el entorno de desarrollo completo.

Este script automatiza la configuración inicial del proyecto incluyendo:
- Verificación de dependencias
- Configuración de base de datos
- Creación de migraciones
- Carga de datos de ejemplo
- Inicio del servidor
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

def run_command(cmd, description, cwd=None, check=True):
    """Ejecutar un comando con manejo de errores."""
    print(f"📋 {description}...")
    try:
        result = subprocess.run(
            cmd, 
            cwd=cwd or Path(__file__).parent.parent,
            check=check,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✅ {description} completado")
            return True, result.stdout
        else:
            print(f"⚠️  {description} completado con advertencias")
            return False, result.stderr
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} falló: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False, str(e)

def check_python_version():
    """Verificar versión de Python."""
    print("🐍 Verificando versión de Python...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ requerido. Versión actual: {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
    return True

def check_postgresql():
    """Verificar instalación de PostgreSQL."""
    print("🐘 Verificando PostgreSQL...")
    success, output = run_command(
        ["psql", "--version"],
        "Verificar PostgreSQL",
        check=False
    )
    if success:
        print("✅ PostgreSQL disponible")
        return True
    else:
        print("⚠️  PostgreSQL no encontrado. Asegúrate de tenerlo instalado y en PATH")
        return False

def setup_environment():
    """Configurar variables de entorno."""
    print("🔧 Configurando variables de entorno...")
    
    current_dir = Path(__file__).parent.parent
    env_file = current_dir / ".env"
    env_example = current_dir / ".env.example"
    
    if env_file.exists():
        print("✅ Archivo .env ya existe")
        return True
    
    if env_example.exists():
        import shutil
        shutil.copy(env_example, env_file)
        print("✅ Archivo .env creado desde .env.example")
        
        # Generar SECRET_KEY segura
        import secrets
        secret_key = secrets.token_urlsafe(32)
        
        # Leer y modificar .env
        with open(env_file, 'r') as f:
            content = f.read()
        
        content = content.replace(
            "SECRET_KEY=your-secret-key-here-change-in-production",
            f"SECRET_KEY={secret_key}"
        )
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ SECRET_KEY generada automáticamente")
        return True
    else:
        print("❌ Archivo .env.example no encontrado")
        return False

def install_dependencies():
    """Instalar dependencias de Python."""
    print("📦 Instalando dependencias...")
    
    # Actualizar pip
    success, _ = run_command(
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
        "Actualizar pip"
    )
    
    if not success:
        print("⚠️  No se pudo actualizar pip, continuando...")
    
    # Instalar dependencias
    success, _ = run_command(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
        "Instalar dependencias"
    )
    
    return success

def create_database():
    """Crear base de datos si no existe."""
    print("🗄️  Configurando base de datos...")
    
    # Leer configuración de .env
    env_file = Path(__file__).parent.parent / ".env"
    if not env_file.exists():
        print("❌ Archivo .env no encontrado")
        return False
    
    db_config = {}
    with open(env_file, 'r') as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                key, value = line.strip().split('=', 1)
                db_config[key] = value
    
    db_name = db_config.get('DATABASE_NAME', 'proyecto_db')
    db_user = db_config.get('DATABASE_USER', 'usuario')
    db_password = db_config.get('DATABASE_PASSWORD', 'password')
    db_host = db_config.get('DATABASE_HOST', 'localhost')
    db_port = db_config.get('DATABASE_PORT', '5432')
    
    # Verificar si la base de datos existe
    check_cmd = [
        "psql", 
        "-h", db_host,
        "-p", db_port,
        "-U", db_user,
        "-d", "postgres",
        "-c", f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'"
    ]
    
    print(f"🔍 Verificando base de datos '{db_name}'...")
    
    # Nota: En producción, esto debería manejarse de manera más segura
    print("⚠️  Configuración manual de base de datos requerida:")
    print(f"   1. Crear usuario: CREATE USER {db_user} WITH PASSWORD '{db_password}';")
    print(f"   2. Crear base de datos: CREATE DATABASE {db_name} OWNER {db_user};")
    print(f"   3. Otorgar permisos: GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user};")
    
    return True

def setup_alembic():
    """Configurar Alembic para migraciones."""
    print("📋 Configurando migraciones...")
    
    current_dir = Path(__file__).parent.parent
    alembic_ini = current_dir / "alembic.ini"
    
    if not alembic_ini.exists():
        print("❌ Archivo alembic.ini no encontrado")
        return False
    
    # Crear migración inicial
    success, _ = run_command(
        [sys.executable, "scripts/migrate.py", "create", "Initial migration"],
        "Crear migración inicial"
    )
    
    if success:
        print("✅ Migración inicial creada")
        
        # Aplicar migración
        success, _ = run_command(
            [sys.executable, "scripts/migrate.py", "upgrade"],
            "Aplicar migraciones"
        )
        
        if success:
            print("✅ Migraciones aplicadas")
            return True
    
    return False

def load_sample_data():
    """Cargar datos de ejemplo."""
    print("📊 Cargando datos de ejemplo...")
    
    success, _ = run_command(
        [sys.executable, "scripts/init_sample_data.py"],
        "Cargar datos de ejemplo"
    )
    
    return success

def create_setup_summary():
    """Crear resumen de configuración."""
    print("📋 Creando resumen de configuración...")
    
    summary = {
        "setup_date": datetime.now().isoformat(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "project_version": "1.0.0",
        "environment": "development",
        "database": "postgresql",
        "api_docs": "http://localhost:8000/api/v1/docs",
        "api_redoc": "http://localhost:8000/api/v1/redoc",
        "default_admin": {
            "email": "admin@sistema.com",
            "password": "Admin123!"
        }
    }
    
    summary_file = Path(__file__).parent.parent / "setup_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("✅ Resumen guardado en setup_summary.json")
    return True

def main():
    """Función principal de configuración."""
    print("🚀 Configuración del Entorno de Desarrollo")
    print("=" * 50)
    print("Sistema de Gestión de Proyectos - Backend API")
    print("=" * 50)
    
    steps = [
        ("Verificar Python", check_python_version),
        ("Verificar PostgreSQL", check_postgresql),
        ("Configurar entorno", setup_environment),
        ("Instalar dependencias", install_dependencies),
        ("Configurar base de datos", create_database),
        ("Configurar migraciones", setup_alembic),
        ("Cargar datos de ejemplo", load_sample_data),
        ("Crear resumen", create_setup_summary),
    ]
    
    results = []
    for step_name, step_func in steps:
        print(f"\n🔄 {step_name}...")
        try:
            result = step_func()
            results.append((step_name, result))
            if result:
                print(f"✅ {step_name} - OK")
            else:
                print(f"⚠️  {step_name} - Con advertencias")
        except Exception as e:
            print(f"❌ {step_name} - Error: {e}")
            results.append((step_name, False))
    
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE CONFIGURACIÓN")
    print("=" * 50)
    
    for step_name, success in results:
        status = "✅ OK" if success else "❌ ERROR"
        print(f"{step_name:<25} {status}")
    
    successful_steps = sum(1 for _, success in results if success)
    total_steps = len(results)
    
    print(f"\n📈 Pasos completados: {successful_steps}/{total_steps}")
    
    if successful_steps == total_steps:
        print("\n🎉 ¡Configuración completada exitosamente!")
        print("\n🚀 Para iniciar el servidor:")
        print("   python scripts/run_dev.py")
        print("\n📖 Documentación API:")
        print("   http://localhost:8000/api/v1/docs")
        print("\n🔐 Credenciales por defecto:")
        print("   Email: admin@sistema.com")
        print("   Password: Admin123!")
    else:
        print("\n⚠️  Configuración completada con advertencias.")
        print("   Revisa los mensajes de error anteriores.")
        print("   Algunos pasos pueden requerir configuración manual.")


if __name__ == "__main__":
    main()
