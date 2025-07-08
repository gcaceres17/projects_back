#!/usr/bin/env python3
"""
Script completo para probar todos los endpoints del sistema
"""
import requests
import json
import time
from datetime import datetime

class APITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.session = requests.Session()
        
    def print_section(self, title):
        """Imprimir una sección con formato"""
        print(f"\n{'='*60}")
        print(f"🧪 {title}")
        print(f"{'='*60}")
    
    def print_test(self, endpoint, method, status_code, response_data=None):
        """Imprimir resultado de un test"""
        status_icon = "✅" if 200 <= status_code < 300 else "❌"
        print(f"{status_icon} {method} {endpoint} - Status: {status_code}")
        
        if response_data and isinstance(response_data, dict):
            if 'message' in response_data:
                print(f"   📝 {response_data['message']}")
            elif 'items' in response_data:
                print(f"   📊 Items encontrados: {len(response_data['items'])}")
            elif 'total' in response_data:
                print(f"   📊 Total: {response_data['total']}")
    
    def test_health(self):
        """Probar endpoint de salud"""
        self.print_section("HEALTH CHECK")
        try:
            response = self.session.get(f"{self.base_url}/health")
            self.print_test("/health", "GET", response.status_code, response.json())
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Error en health check: {e}")
            return False
    
    def test_authentication(self):
        """Probar autenticación"""
        self.print_section("AUTENTICACIÓN")
        
        # Test login con credenciales correctas
        login_data = {
            "username": "admin@sistema.com",
            "password": "Admin123!"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/login", 
                data=login_data
            )
            self.print_test("/api/v1/auth/login", "POST", response.status_code)
            
            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                print(f"   🔑 Token obtenido exitosamente")
                return True
            else:
                print(f"   ❌ Error en login: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error en autenticación: {e}")
            return False
    
    def test_colaboradores(self):
        """Probar endpoints de colaboradores"""
        self.print_section("COLABORADORES")
        
        try:
            # GET /colaboradores
            response = self.session.get(f"{self.base_url}/api/v1/colaboradores")
            self.print_test("/api/v1/colaboradores", "GET", response.status_code, response.json())
            
            # GET /colaboradores/estadisticas
            response = self.session.get(f"{self.base_url}/api/v1/colaboradores/estadisticas")
            self.print_test("/api/v1/colaboradores/estadisticas", "GET", response.status_code, response.json())
            
            # GET /colaboradores con filtros
            response = self.session.get(f"{self.base_url}/api/v1/colaboradores?departamento=Desarrollo")
            self.print_test("/api/v1/colaboradores?departamento=Desarrollo", "GET", response.status_code, response.json())
            
            # POST /colaboradores (crear nuevo)
            nuevo_colaborador = {
                "nombre": "Test",
                "apellido": "Usuario",
                "email": f"test.{int(time.time())}@test.com",
                "tipo_colaborador": "interno",
                "departamento": "Testing",
                "cargo": "Tester",
                "habilidades": ["Testing", "Automation"],
                "costo_hora": 15000.00
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/colaboradores", 
                json=nuevo_colaborador
            )
            self.print_test("/api/v1/colaboradores", "POST", response.status_code, response.json())
            
            if response.status_code == 201:
                colaborador_id = response.json().get("id")
                print(f"   🆕 Colaborador creado con ID: {colaborador_id}")
                
                # GET /colaboradores/{id}
                response = self.session.get(f"{self.base_url}/api/v1/colaboradores/{colaborador_id}")
                self.print_test(f"/api/v1/colaboradores/{colaborador_id}", "GET", response.status_code)
                
                # PUT /colaboradores/{id}
                colaborador_actualizado = nuevo_colaborador.copy()
                colaborador_actualizado["cargo"] = "Senior Tester"
                
                response = self.session.put(
                    f"{self.base_url}/api/v1/colaboradores/{colaborador_id}",
                    json=colaborador_actualizado
                )
                self.print_test(f"/api/v1/colaboradores/{colaborador_id}", "PUT", response.status_code)
                
        except Exception as e:
            print(f"❌ Error en colaboradores: {e}")
    
    def test_proyectos(self):
        """Probar endpoints de proyectos"""
        self.print_section("PROYECTOS")
        
        try:
            # GET /proyectos
            response = self.session.get(f"{self.base_url}/api/v1/proyectos")
            self.print_test("/api/v1/proyectos", "GET", response.status_code, response.json())
            
            # GET /proyectos/estadisticas
            response = self.session.get(f"{self.base_url}/api/v1/proyectos/estadisticas")
            self.print_test("/api/v1/proyectos/estadisticas", "GET", response.status_code, response.json())
            
            # GET /proyectos con filtros
            response = self.session.get(f"{self.base_url}/api/v1/proyectos?estado=en_progreso")
            self.print_test("/api/v1/proyectos?estado=en_progreso", "GET", response.status_code, response.json())
            
            # POST /proyectos (crear nuevo)
            nuevo_proyecto = {
                "nombre": f"Proyecto Test {int(time.time())}",
                "descripcion": "Proyecto creado para testing",
                "cliente_id": 1,
                "estado": "planificacion",
                "prioridad": "media",
                "fecha_inicio": "2024-07-08",
                "fecha_fin_estimada": "2024-12-31",
                "presupuesto": 10000000.00,
                "horas_estimadas": 100
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/proyectos",
                json=nuevo_proyecto
            )
            self.print_test("/api/v1/proyectos", "POST", response.status_code, response.json())
            
            if response.status_code == 201:
                proyecto_id = response.json().get("id")
                print(f"   🆕 Proyecto creado con ID: {proyecto_id}")
                
                # GET /proyectos/{id}
                response = self.session.get(f"{self.base_url}/api/v1/proyectos/{proyecto_id}")
                self.print_test(f"/api/v1/proyectos/{proyecto_id}", "GET", response.status_code)
                
        except Exception as e:
            print(f"❌ Error en proyectos: {e}")
    
    def test_clientes(self):
        """Probar endpoints de clientes"""
        self.print_section("CLIENTES")
        
        try:
            # GET /clientes
            response = self.session.get(f"{self.base_url}/api/v1/clientes")
            self.print_test("/api/v1/clientes", "GET", response.status_code, response.json())
            
            # POST /clientes (crear nuevo)
            nuevo_cliente = {
                "nombre": f"Cliente Test {int(time.time())}",
                "email": f"cliente.{int(time.time())}@test.com",
                "telefono": "+57 300 123 4567",
                "ciudad": "Bogotá",
                "tipo_cliente": "empresa"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/clientes",
                json=nuevo_cliente
            )
            self.print_test("/api/v1/clientes", "POST", response.status_code, response.json())
            
        except Exception as e:
            print(f"❌ Error en clientes: {e}")
    
    def test_cotizaciones(self):
        """Probar endpoints de cotizaciones"""
        self.print_section("COTIZACIONES")
        
        try:
            # GET /cotizaciones
            response = self.session.get(f"{self.base_url}/api/v1/cotizaciones")
            self.print_test("/api/v1/cotizaciones", "GET", response.status_code, response.json())
            
            # POST /cotizaciones (crear nueva)
            nueva_cotizacion = {
                "cliente_id": 1,
                "proyecto_id": 1,
                "fecha_vencimiento": "2024-08-31",
                "observaciones": "Cotización de prueba",
                "items": [
                    {
                        "descripcion": "Desarrollo web",
                        "cantidad": 1,
                        "precio_unitario": 5000000.00
                    },
                    {
                        "descripcion": "Testing",
                        "cantidad": 1,
                        "precio_unitario": 1000000.00
                    }
                ]
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/cotizaciones",
                json=nueva_cotizacion
            )
            self.print_test("/api/v1/cotizaciones", "POST", response.status_code, response.json())
            
        except Exception as e:
            print(f"❌ Error en cotizaciones: {e}")
    
    def test_costos_rigidos(self):
        """Probar endpoints de costos rígidos"""
        self.print_section("COSTOS RÍGIDOS")
        
        try:
            # GET /costos-rigidos
            response = self.session.get(f"{self.base_url}/api/v1/costos-rigidos")
            self.print_test("/api/v1/costos-rigidos", "GET", response.status_code, response.json())
            
            # GET /costos-rigidos/estadisticas
            response = self.session.get(f"{self.base_url}/api/v1/costos-rigidos/estadisticas")
            self.print_test("/api/v1/costos-rigidos/estadisticas", "GET", response.status_code, response.json())
            
            # POST /costos-rigidos (crear nuevo)
            nuevo_costo = {
                "nombre": "Servidor de testing",
                "descripcion": "Costo de servidor para pruebas",
                "categoria": "Infraestructura",
                "tipo": "fijo",
                "monto": 500000.00,
                "frecuencia": "mensual",
                "proveedor": "AWS",
                "proyecto_id": 1,
                "fecha_inicio": "2024-07-01"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/costos-rigidos",
                json=nuevo_costo
            )
            self.print_test("/api/v1/costos-rigidos", "POST", response.status_code, response.json())
            
        except Exception as e:
            print(f"❌ Error en costos rígidos: {e}")
    
    def test_reportes(self):
        """Probar endpoints de reportes"""
        self.print_section("REPORTES")
        
        try:
            # GET /reportes/dashboard
            response = self.session.get(f"{self.base_url}/api/v1/reportes/dashboard")
            self.print_test("/api/v1/reportes/dashboard", "GET", response.status_code, response.json())
            
            # GET /reportes/proyectos
            response = self.session.get(f"{self.base_url}/api/v1/reportes/proyectos")
            self.print_test("/api/v1/reportes/proyectos", "GET", response.status_code, response.json())
            
        except Exception as e:
            print(f"❌ Error en reportes: {e}")
    
    def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        print("🚀 INICIANDO PRUEBAS COMPLETAS DE ENDPOINTS")
        print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 Base URL: {self.base_url}")
        
        # Test de salud primero
        if not self.test_health():
            print("❌ El servidor no está disponible. Verifica que esté ejecutándose.")
            return
        
        # Test de autenticación
        if not self.test_authentication():
            print("❌ No se pudo autenticar. Continuando con endpoints públicos.")
        
        # Ejecutar todas las pruebas
        self.test_colaboradores()
        self.test_proyectos()
        self.test_clientes()
        self.test_cotizaciones()
        self.test_costos_rigidos()
        self.test_reportes()
        
        self.print_section("RESUMEN")
        print("✅ Pruebas completadas")
        print("📚 Para ver la documentación completa: http://localhost:8000/api/v1/docs")
        print("🔍 Para probar manualmente: http://localhost:8000/api/v1/redoc")

if __name__ == "__main__":
    tester = APITester()
    tester.run_all_tests()
