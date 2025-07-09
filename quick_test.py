import requests
import json

def test_server():
    try:
        # Verificar salud del servidor
        response = requests.get("http://localhost:8000/health")
        print(f"Health check: {response.status_code}")
        if response.status_code == 200:
            print("✅ Servidor funcionando")
            print(json.dumps(response.json(), indent=2))
        else:
            print("❌ Error en servidor")
            
        # Verificar documentación
        response = requests.get("http://localhost:8000/api/v1/docs")
        print(f"Documentación: {response.status_code}")
        
        # Verificar autenticación
        login_data = {"email": "admin@sistema.com", "password": "admin123"}
        response = requests.post("http://localhost:8000/api/v1/auth/login", json=login_data)
        print(f"Login: {response.status_code}")
        
        if response.status_code == 200:
            token = response.json().get('access_token')
            print(f"Token: {token[:50]}...")
            
            # Verificar colaboradores
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get("http://localhost:8000/api/v1/colaboradores", headers=headers)
            print(f"Colaboradores: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_server()
