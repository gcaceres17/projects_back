#!/usr/bin/env python3
"""
Archivo de inicio directo para el servidor FastAPI.

Este archivo permite iniciar rápidamente el servidor sin scripts adicionales.
"""

if __name__ == "__main__":
    import uvicorn
    import sys
    import os
    from pathlib import Path
    
    # Agregar el directorio actual al PYTHONPATH
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    # Configurar variables de entorno desde .env si existe
    env_file = current_dir / ".env"
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(env_file)
    
    print("🚀 Iniciando servidor FastAPI...")
    print("📍 API: http://localhost:8000")
    print("📖 Docs: http://localhost:8000/api/v1/docs")
    print("🛑 Presiona Ctrl+C para detener")
    print("=" * 50)
    
    # Iniciar servidor
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["app"],
        log_level="info"
    )
