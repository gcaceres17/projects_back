#!/usr/bin/env python3
"""
Script de prueba simplificado para verificar el backend.
"""

import requests
import json
import time
import sys
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"

def test_health():
    """Verificar que el servidor esté funcionando."""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Servidor funcionando correctamente")
            data = response.json()
            print(f"   - Status: {data.get('status')}")
            print(f"   - Version: {data.get('version')}")
            return True
        else:
            print(f"❌ Error en health check: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando al servidor: {e}")
        return False

def test_auth():
    """Probar autenticación."""
    try:
        # Intentar login con credenciales por defecto
        login_data = {
            "email": "admin@sistema.com",
            "password": "admin123"
        }
        
        response = requests.post(f"{API_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            print("✅ Autenticación exitosa")
            data = response.json()
            token = data.get('access_token')
            print(f"   - Token obtenido: {token[:50]}...")
            return token
        else:
            print(f"❌ Error en autenticación: {response.status_code}")
            if response.status_code == 401:
                print("   - Credenciales inválidas")
            return None
    except Exception as e:
        print(f"❌ Error en autenticación: {e}")
        return None

def test_endpoints_with_token(token):
    """Probar endpoints principales con token."""
    if not token:
        print("❌ No se puede probar endpoints sin token")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    endpoints = [
        ("GET", "/colaboradores", "Listar colaboradores"),
        ("GET", "/proyectos", "Listar proyectos"),
        ("GET", "/clientes", "Listar clientes"),
        ("GET", "/cotizaciones", "Listar cotizaciones"),
        ("GET", "/costos-rigidos", "Listar costos rígidos"),
        ("GET", "/reportes/dashboard", "Dashboard de reportes"),
    ]
    
    success_count = 0
    
    for method, endpoint, description in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{API_URL}{endpoint}", headers=headers)
            
            if response.status_code == 200:
                print(f"✅ {description}")
                success_count += 1
            else:
                print(f"❌ {description}: {response.status_code}")
        except Exception as e:
            print(f"❌ {description}: Error - {e}")
    
    print(f"\n📊 Resumen: {success_count}/{len(endpoints)} endpoints funcionando")
    return success_count == len(endpoints)

def test_create_operations(token):
    """Probar operaciones de creación."""
    if not token:
        print("❌ No se puede probar creación sin token")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Crear colaborador
    try:
        colaborador_data = {
            "nombre": "Juan",
            "apellido": "Pérez",
            "email": "juan.perez@test.com",
            "telefono": "123456789",
            "cargo": "Desarrollador",
            "salario": 3000000,
            "fecha_ingreso": "2024-01-01",
            "tipo": "interno"
        }
        
        response = requests.post(f"{API_URL}/colaboradores", json=colaborador_data, headers=headers)
        if response.status_code == 201:
            print("✅ Creación de colaborador exitosa")
            colaborador = response.json()
            
            # Crear cliente
            cliente_data = {
                "nombre": "Empresa Test",
                "email": "contacto@empresatest.com",
                "telefono": "987654321",
                "direccion": "Calle Test 123",
                "ciudad": "Bogotá",
                "pais": "Colombia"
            }
            
            response = requests.post(f"{API_URL}/clientes", json=cliente_data, headers=headers)
            if response.status_code == 201:
                print("✅ Creación de cliente exitosa")
                cliente = response.json()
                
                # Crear proyecto
                proyecto_data = {
                    "nombre": "Proyecto Test",
                    "descripcion": "Proyecto de prueba",
                    "fecha_inicio": "2024-01-01",
                    "fecha_fin": "2024-12-31",
                    "presupuesto": 10000000,
                    "cliente_id": cliente["id"],
                    "colaborador_responsable_id": colaborador["id"]
                }
                
                response = requests.post(f"{API_URL}/proyectos", json=proyecto_data, headers=headers)
                if response.status_code == 201:
                    print("✅ Creación de proyecto exitosa")
                    return True
                else:
                    print(f"❌ Error creando proyecto: {response.status_code}")
            else:
                print(f"❌ Error creando cliente: {response.status_code}")
        else:
            print(f"❌ Error creando colaborador: {response.status_code}")
    except Exception as e:
        print(f"❌ Error en operaciones de creación: {e}")
    
    return False

def main():
    """Función principal de prueba."""
    print("🚀 Iniciando pruebas del backend...")
    print("=" * 50)
    
    # Paso 1: Verificar que el servidor esté funcionando
    if not test_health():
        print("❌ El servidor no está funcionando. Abortando pruebas.")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    
    # Paso 2: Probar autenticación
    token = test_auth()
    
    print("\n" + "=" * 50)
    
    # Paso 3: Probar endpoints principales
    if test_endpoints_with_token(token):
        print("✅ Todos los endpoints principales funcionan correctamente")
    else:
        print("⚠️  Algunos endpoints tienen problemas")
    
    print("\n" + "=" * 50)
    
    # Paso 4: Probar operaciones de creación
    if test_create_operations(token):
        print("✅ Operaciones de creación funcionan correctamente")
    else:
        print("⚠️  Problemas con operaciones de creación")
    
    print("\n" + "=" * 50)
    print("🎉 Pruebas completadas!")
    print(f"🌐 Documentación disponible en: {BASE_URL}/api/v1/docs")

if __name__ == "__main__":
    main()
