#!/usr/bin/env python3
"""
Script para ejecutar el servidor de desarrollo.

Este script facilita el inicio del servidor FastAPI con configuración
optimizada para desarrollo.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Iniciar el servidor de desarrollo."""
    print("🚀 Iniciando servidor de desarrollo...")
    print("=" * 50)
    
    # Verificar que estamos en el directorio correcto
    current_dir = Path(__file__).parent.parent
    os.chdir(current_dir)
    
    # Verificar que existe el archivo .env
    env_file = current_dir / ".env"
    if not env_file.exists():
        print("⚠️  Archivo .env no encontrado. Copiando desde .env.example...")
        env_example = current_dir / ".env.example"
        if env_example.exists():
            import shutil
            shutil.copy(env_example, env_file)
            print("✓ Archivo .env creado. Por favor, configura tus variables de entorno.")
        else:
            print("❌ Archivo .env.example no encontrado. Creando .env básico...")
            with open(env_file, 'w') as f:
                f.write("""# Database Configuration
DATABASE_URL=postgresql://usuario:password@localhost/proyecto_db
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=proyecto_db
DATABASE_USER=usuario
DATABASE_PASSWORD=password

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=development
DEBUG=true

# API Configuration
API_V1_STR=/api/v1
PROJECT_NAME=Sistema de Gestión de Proyectos
PROJECT_VERSION=1.0.0

# CORS Configuration
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:3001"]
""")
    
    # Verificar que el entorno virtual está activado
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Entorno virtual no activado. Asegúrate de activar el entorno virtual.")
        print("   Windows: .venv\\Scripts\\activate")
        print("   Linux/Mac: source .venv/bin/activate")
    
    # Comandos para ejecutar
    commands = [
        {
            "name": "Instalar dependencias",
            "cmd": [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            "optional": True
        },
        {
            "name": "Iniciar servidor",
            "cmd": [
                sys.executable, "-m", "uvicorn", "app.main:app",
                "--host", "0.0.0.0",
                "--port", "8000",
                "--reload",
                "--reload-dir", "app",
                "--log-level", "info"
            ],
            "optional": False
        }
    ]
    
    for command in commands:
        print(f"\n📋 {command['name']}...")
        try:
            result = subprocess.run(
                command["cmd"],
                cwd=current_dir,
                check=True if not command["optional"] else False
            )
            if result.returncode == 0:
                print(f"✅ {command['name']} completado")
            else:
                print(f"⚠️  {command['name']} terminó con advertencias")
        except subprocess.CalledProcessError as e:
            if command["optional"]:
                print(f"⚠️  {command['name']} falló (opcional): {e}")
            else:
                print(f"❌ {command['name']} falló: {e}")
                sys.exit(1)
        except KeyboardInterrupt:
            print(f"\n🛑 {command['name']} interrumpido por usuario")
            sys.exit(0)
    
    print("\n🎉 Servidor iniciado exitosamente!")
    print("📍 API disponible en: http://localhost:8000")
    print("📖 Documentación en: http://localhost:8000/api/v1/docs")
    print("🔧 Redoc en: http://localhost:8000/api/v1/redoc")
    print("\n🛑 Presiona Ctrl+C para detener el servidor")


if __name__ == "__main__":
    main()
