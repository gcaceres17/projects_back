#!/usr/bin/env python3
"""
Script para iniciar el servidor de desarrollo
"""
import uvicorn
from app.main import app

if __name__ == "__main__":
    print("🚀 Iniciando servidor FastAPI...")
    print("📍 URL: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/api/v1/docs")
    print("❌ Para detener: Ctrl+C")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )
