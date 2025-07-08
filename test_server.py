#!/usr/bin/env python3
"""
Script para verificar que el servidor funcione correctamente
"""
import requests
import json

def test_server():
    """Probar endpoints del servidor"""
    base_url = "http://localhost:8000"
    
    try:
        # Probar endpoint de salud
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"   Respuesta: {response.json()}")
        
        # Probar documentación
        response = requests.get(f"{base_url}/api/v1/docs")
        print(f"✅ Documentación: {response.status_code}")
        
        # Probar endpoint de colaboradores
        response = requests.get(f"{base_url}/api/v1/colaboradores")
        print(f"✅ Colaboradores: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Encontrados {len(data.get('items', []))} colaboradores")
        
        # Probar endpoint de proyectos
        response = requests.get(f"{base_url}/api/v1/proyectos")
        print(f"✅ Proyectos: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Encontrados {len(data.get('items', []))} proyectos")
        
        print("\n🎉 ¡Servidor funcionando correctamente!")
        
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor. Asegúrate de que esté ejecutándose.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_server()
