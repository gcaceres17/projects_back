#!/usr/bin/env python3
"""
Script de validación rápida del sistema.
Verifica que todos los componentes estén funcionando correctamente.
"""

import requests
import json
import sys
from datetime import datetime

def print_header(title):
    """Imprime un header formateado."""
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")

def print_status(description, status, details=None):
    """Imprime el estado de una verificación."""
    icon = "✅" if status else "❌"
    print(f"{icon} {description}")
    if details:
        print(f"   {details}")

def check_api_health():
    """Verifica el health check de la API."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return True, f"Status: {data.get('status')}, Version: {data.get('version')}"
        else:
            return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, str(e)

def check_api_docs():
    """Verifica que la documentación esté disponible."""
    try:
        response = requests.get("http://localhost:8000/api/v1/docs", timeout=5)
        return response.status_code == 200, f"HTTP {response.status_code}"
    except Exception as e:
        return False, str(e)

def check_authentication():
    """Verifica el sistema de autenticación."""
    try:
        login_data = {
            "email": "admin@sistema.com",
            "password": "admin123"
        }
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login", 
            json=login_data, 
            timeout=5
        )
        if response.status_code == 200:
            token = response.json().get('access_token')
            return True, f"Token obtenido: {token[:20]}..."
        else:
            return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, str(e)

def check_endpoints(token):
    """Verifica endpoints principales con autenticación."""
    headers = {"Authorization": f"Bearer {token}"}
    endpoints = [
        ("GET", "/colaboradores", "Colaboradores"),
        ("GET", "/proyectos", "Proyectos"),
        ("GET", "/clientes", "Clientes"),
        ("GET", "/cotizaciones", "Cotizaciones"),
        ("GET", "/costos-rigidos", "Costos Rígidos"),
        ("GET", "/reportes/dashboard", "Dashboard"),
    ]
    
    results = []
    for method, endpoint, name in endpoints:
        try:
            url = f"http://localhost:8000/api/v1{endpoint}"
            response = requests.get(url, headers=headers, timeout=5)
            success = response.status_code == 200
            details = f"HTTP {response.status_code}"
            results.append((name, success, details))
        except Exception as e:
            results.append((name, False, str(e)))
    
    return results

def main():
    """Función principal."""
    print_header("VALIDACIÓN DEL SISTEMA")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Verificar health check
    print_header("1. VERIFICACIÓN DE SALUD")
    health_ok, health_details = check_api_health()
    print_status("API Health Check", health_ok, health_details)
    
    if not health_ok:
        print("\n❌ La API no está disponible. Verifica que esté ejecutándose.")
        print("   Comando: docker-compose up -d")
        sys.exit(1)
    
    # 2. Verificar documentación
    print_header("2. VERIFICACIÓN DE DOCUMENTACIÓN")
    docs_ok, docs_details = check_api_docs()
    print_status("Documentación Swagger", docs_ok, docs_details)
    
    # 3. Verificar autenticación
    print_header("3. VERIFICACIÓN DE AUTENTICACIÓN")
    auth_ok, auth_details = check_authentication()
    print_status("Sistema de Login", auth_ok, auth_details)
    
    if not auth_ok:
        print("\n❌ La autenticación falló.")
        sys.exit(1)
    
    # Extraer token para siguientes pruebas
    token = auth_details.split(": ")[1].replace("...", "")
    
    # 4. Verificar endpoints principales
    print_header("4. VERIFICACIÓN DE ENDPOINTS")
    endpoint_results = check_endpoints(token)
    
    success_count = 0
    for name, success, details in endpoint_results:
        print_status(f"Endpoint {name}", success, details)
        if success:
            success_count += 1
    
    # 5. Resumen final
    print_header("RESUMEN FINAL")
    total_checks = len(endpoint_results) + 3  # health, docs, auth
    passed_checks = success_count + (1 if health_ok else 0) + (1 if docs_ok else 0) + (1 if auth_ok else 0)
    
    print(f"✅ Verificaciones exitosas: {passed_checks}/{total_checks}")
    
    if passed_checks == total_checks:
        print("🎉 SISTEMA COMPLETAMENTE FUNCIONAL")
        print("\n📖 Accede a la documentación: http://localhost:8000/api/v1/docs")
        print("🔐 Credenciales: admin@sistema.com / admin123")
    else:
        print("⚠️  Algunos componentes requieren atención")
        sys.exit(1)

if __name__ == "__main__":
    main()
