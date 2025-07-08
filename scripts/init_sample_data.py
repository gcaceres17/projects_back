"""
Script para inicializar la base de datos con datos de ejemplo.

Este script crea:
- Usuarios de ejemplo
- Clientes de ejemplo
- Colaboradores de ejemplo
- Proyectos de ejemplo
- Cotizaciones de ejemplo
- Costos rígidos de ejemplo
"""

import sys
import os
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, create_tables
from app.models import (
    Usuario, Cliente, Colaborador, Proyecto, Cotizacion, ItemCotizacion,
    CostoRigido, EstadoProyecto, EstadoCotizacion, TipoColaborador, TipoCosto
)
from app.auth import get_password_hash


def create_sample_users(db: Session):
    """Crear usuarios de ejemplo."""
    print("Creando usuarios de ejemplo...")
    
    users = [
        {
            "email": "admin@sistema.com",
            "nombre": "Administrador",
            "apellido": "Sistema",
            "password": "Admin123!",
            "es_admin": True
        },
        {
            "email": "gerente@sistema.com",
            "nombre": "Juan",
            "apellido": "Pérez",
            "password": "Gerente123!",
            "es_admin": False
        },
        {
            "email": "usuario@sistema.com",
            "nombre": "Ana",
            "apellido": "García",
            "password": "Usuario123!",
            "es_admin": False
        }
    ]
    
    for user_data in users:
        existing_user = db.query(Usuario).filter(Usuario.email == user_data["email"]).first()
        if not existing_user:
            user = Usuario(
                email=user_data["email"],
                nombre=user_data["nombre"],
                apellido=user_data["apellido"],
                hashed_password=get_password_hash(user_data["password"]),
                es_admin=user_data["es_admin"],
                activo=True
            )
            db.add(user)
    
    db.commit()
    print(f"✓ {len(users)} usuarios creados")


def create_sample_clients(db: Session):
    """Crear clientes de ejemplo."""
    print("Creando clientes de ejemplo...")
    
    clients = [
        {
            "nombre": "Empresa ABC S.A.S.",
            "email": "contacto@empresaabc.com",
            "telefono": "+57 301 234 5678",
            "direccion": "Calle 123 #45-67, Bogotá",
            "ciudad": "Bogotá",
            "pais": "Colombia",
            "contacto_principal": "Carlos Rodríguez",
            "nit_ruc": "900123456-7"
        },
        {
            "nombre": "Tecnología XYZ Ltda.",
            "email": "info@tecnologiaxyz.com",
            "telefono": "+57 302 345 6789",
            "direccion": "Carrera 15 #30-45, Medellín",
            "ciudad": "Medellín",
            "pais": "Colombia",
            "contacto_principal": "María López",
            "nit_ruc": "800234567-8"
        },
        {
            "nombre": "Innovación Digital Corp.",
            "email": "ventas@innovaciondigital.com",
            "telefono": "+57 303 456 7890",
            "direccion": "Avenida 68 #40-50, Cali",
            "ciudad": "Cali",
            "pais": "Colombia",
            "contacto_principal": "Pedro Martínez",
            "nit_ruc": "700345678-9"
        }
    ]
    
    for client_data in clients:
        existing_client = db.query(Cliente).filter(Cliente.email == client_data["email"]).first()
        if not existing_client:
            client = Cliente(**client_data)
            db.add(client)
    
    db.commit()
    print(f"✓ {len(clients)} clientes creados")


def create_sample_collaborators(db: Session):
    """Crear colaboradores de ejemplo."""
    print("Creando colaboradores de ejemplo...")
    
    collaborators = [
        {
            "nombre": "Luis",
            "apellido": "González",
            "email": "luis.gonzalez@empresa.com",
            "telefono": "+57 310 123 4567",
            "cargo": "Desarrollador Senior",
            "departamento": "Desarrollo",
            "tipo": TipoColaborador.INTERNO,
            "costo_hora": 25000,
            "habilidades": "Python, JavaScript, React, PostgreSQL"
        },
        {
            "nombre": "Sofia",
            "apellido": "Ramírez",
            "email": "sofia.ramirez@empresa.com",
            "telefono": "+57 311 234 5678",
            "cargo": "Diseñadora UX/UI",
            "departamento": "Diseño",
            "tipo": TipoColaborador.INTERNO,
            "costo_hora": 22000,
            "habilidades": "Figma, Adobe XD, Photoshop, Illustrator"
        },
        {
            "nombre": "Carlos",
            "apellido": "Mendoza",
            "email": "carlos.mendoza@freelance.com",
            "telefono": "+57 312 345 6789",
            "cargo": "Consultor DevOps",
            "departamento": "Infraestructura",
            "tipo": TipoColaborador.FREELANCE,
            "costo_hora": 35000,
            "habilidades": "Docker, Kubernetes, AWS, Jenkins"
        },
        {
            "nombre": "Elena",
            "apellido": "Torres",
            "email": "elena.torres@empresa.com",
            "telefono": "+57 313 456 7890",
            "cargo": "Analista de Sistemas",
            "departamento": "Análisis",
            "tipo": TipoColaborador.INTERNO,
            "costo_hora": 20000,
            "habilidades": "SQL, Power BI, Excel, Python"
        },
        {
            "nombre": "Miguel",
            "apellido": "Vargas",
            "email": "miguel.vargas@externo.com",
            "telefono": "+57 314 567 8901",
            "cargo": "Especialista en Seguridad",
            "departamento": "Seguridad",
            "tipo": TipoColaborador.EXTERNO,
            "costo_hora": 30000,
            "habilidades": "Pentesting, OWASP, Kali Linux, Nessus"
        }
    ]
    
    for collab_data in collaborators:
        existing_collab = db.query(Colaborador).filter(
            Colaborador.email == collab_data["email"]
        ).first()
        if not existing_collab:
            collaborator = Colaborador(**collab_data)
            db.add(collaborator)
    
    db.commit()
    print(f"✓ {len(collaborators)} colaboradores creados")


def create_sample_projects(db: Session):
    """Crear proyectos de ejemplo."""
    print("Creando proyectos de ejemplo...")
    
    # Obtener clientes y colaboradores
    clients = db.query(Cliente).all()
    collaborators = db.query(Colaborador).all()
    
    if not clients or not collaborators:
        print("⚠️  No se pueden crear proyectos sin clientes y colaboradores")
        return
    
    projects = [
        {
            "nombre": "Sistema de Gestión Empresarial",
            "descripcion": "Desarrollo de un sistema completo para gestión empresarial con módulos de facturación, inventario y CRM.",
            "cliente_id": clients[0].id,
            "estado": EstadoProyecto.EN_PROGRESO,
            "fecha_inicio": datetime.now() - timedelta(days=30),
            "fecha_fin_estimada": datetime.now() + timedelta(days=60),
            "presupuesto": 50000000,
            "costo_real": 25000000,
            "horas_estimadas": 800,
            "horas_trabajadas": 450,
            "progreso": 60,
            "prioridad": 1,
            "notas": "Proyecto estratégico para el cliente principal"
        },
        {
            "nombre": "App Mobile E-commerce",
            "descripcion": "Desarrollo de aplicación móvil para comercio electrónico con integración de pagos y notificaciones push.",
            "cliente_id": clients[1].id,
            "estado": EstadoProyecto.PLANIFICACION,
            "fecha_inicio": datetime.now() + timedelta(days=15),
            "fecha_fin_estimada": datetime.now() + timedelta(days=105),
            "presupuesto": 35000000,
            "costo_real": 0,
            "horas_estimadas": 600,
            "horas_trabajadas": 0,
            "progreso": 15,
            "prioridad": 2,
            "notas": "Proyecto en fase de planificación y diseño"
        },
        {
            "nombre": "Migración a la Nube",
            "descripcion": "Migración de infraestructura local a AWS con implementación de mejores prácticas de seguridad.",
            "cliente_id": clients[2].id,
            "estado": EstadoProyecto.COMPLETADO,
            "fecha_inicio": datetime.now() - timedelta(days=90),
            "fecha_fin_estimada": datetime.now() - timedelta(days=30),
            "fecha_fin_real": datetime.now() - timedelta(days=15),
            "presupuesto": 28000000,
            "costo_real": 26500000,
            "horas_estimadas": 400,
            "horas_trabajadas": 385,
            "progreso": 100,
            "prioridad": 1,
            "notas": "Proyecto completado exitosamente"
        }
    ]
    
    created_projects = []
    for project_data in projects:
        existing_project = db.query(Proyecto).filter(
            Proyecto.nombre == project_data["nombre"]
        ).first()
        if not existing_project:
            project = Proyecto(**project_data)
            db.add(project)
            db.flush()  # Para obtener el ID
            
            # Asignar colaboradores aleatorios
            num_collaborators = random.randint(2, 4)
            selected_collaborators = random.sample(collaborators, num_collaborators)
            project.colaboradores.extend(selected_collaborators)
            
            created_projects.append(project)
    
    db.commit()
    print(f"✓ {len(created_projects)} proyectos creados")


def create_sample_quotations(db: Session):
    """Crear cotizaciones de ejemplo."""
    print("Creando cotizaciones de ejemplo...")
    
    # Obtener clientes y proyectos
    clients = db.query(Cliente).all()
    projects = db.query(Proyecto).all()
    
    if not clients:
        print("⚠️  No se pueden crear cotizaciones sin clientes")
        return
    
    quotations = [
        {
            "numero": "COT-2024-001",
            "cliente_id": clients[0].id,
            "proyecto_id": projects[0].id if projects else None,
            "titulo": "Cotización Sistema de Gestión Empresarial",
            "descripcion": "Desarrollo completo de sistema empresarial con módulos integrados",
            "estado": EstadoCotizacion.APROBADA,
            "fecha_vencimiento": datetime.now() + timedelta(days=30),
            "validez_dias": 30,
            "descuento": 5.0,
            "terminos_condiciones": "Pago 50% al inicio, 50% al finalizar. Incluye 3 meses de soporte."
        },
        {
            "numero": "COT-2024-002",
            "cliente_id": clients[1].id,
            "proyecto_id": projects[1].id if len(projects) > 1 else None,
            "titulo": "Cotización App Mobile E-commerce",
            "descripcion": "Desarrollo de aplicación móvil multiplataforma para comercio electrónico",
            "estado": EstadoCotizacion.ENVIADA,
            "fecha_vencimiento": datetime.now() + timedelta(days=15),
            "validez_dias": 15,
            "descuento": 0.0,
            "terminos_condiciones": "Pago 30% al inicio, 40% en hito intermedio, 30% al finalizar."
        },
        {
            "numero": "COT-2024-003",
            "cliente_id": clients[2].id,
            "titulo": "Cotización Consultoría Digital",
            "descripcion": "Consultoría para transformación digital y optimización de procesos",
            "estado": EstadoCotizacion.BORRADOR,
            "fecha_vencimiento": datetime.now() + timedelta(days=45),
            "validez_dias": 45,
            "descuento": 10.0,
            "terminos_condiciones": "Pago contra entrega de hitos definidos."
        }
    ]
    
    created_quotations = []
    for quot_data in quotations:
        existing_quot = db.query(Cotizacion).filter(
            Cotizacion.numero == quot_data["numero"]
        ).first()
        if not existing_quot:
            quotation = Cotizacion(**quot_data)
            db.add(quotation)
            db.flush()  # Para obtener el ID
            
            # Crear items de cotización
            if quot_data["numero"] == "COT-2024-001":
                items = [
                    {
                        "descripcion": "Desarrollo módulo de facturación",
                        "cantidad": 1,
                        "precio_unitario": 15000000,
                        "subtotal": 15000000,
                        "orden": 1
                    },
                    {
                        "descripcion": "Desarrollo módulo de inventario",
                        "cantidad": 1,
                        "precio_unitario": 12000000,
                        "subtotal": 12000000,
                        "orden": 2
                    },
                    {
                        "descripcion": "Desarrollo módulo CRM",
                        "cantidad": 1,
                        "precio_unitario": 18000000,
                        "subtotal": 18000000,
                        "orden": 3
                    },
                    {
                        "descripcion": "Integración y pruebas",
                        "cantidad": 1,
                        "precio_unitario": 8000000,
                        "subtotal": 8000000,
                        "orden": 4
                    }
                ]
            elif quot_data["numero"] == "COT-2024-002":
                items = [
                    {
                        "descripcion": "Desarrollo app Android",
                        "cantidad": 1,
                        "precio_unitario": 18000000,
                        "subtotal": 18000000,
                        "orden": 1
                    },
                    {
                        "descripcion": "Desarrollo app iOS",
                        "cantidad": 1,
                        "precio_unitario": 20000000,
                        "subtotal": 20000000,
                        "orden": 2
                    },
                    {
                        "descripcion": "Backend API REST",
                        "cantidad": 1,
                        "precio_unitario": 15000000,
                        "subtotal": 15000000,
                        "orden": 3
                    }
                ]
            else:
                items = [
                    {
                        "descripcion": "Consultoría y análisis",
                        "cantidad": 40,
                        "precio_unitario": 200000,
                        "subtotal": 8000000,
                        "orden": 1
                    },
                    {
                        "descripcion": "Implementación de mejoras",
                        "cantidad": 1,
                        "precio_unitario": 12000000,
                        "subtotal": 12000000,
                        "orden": 2
                    }
                ]
            
            for item_data in items:
                item_data["cotizacion_id"] = quotation.id
                item = ItemCotizacion(**item_data)
                db.add(item)
            
            # Calcular totales
            subtotal = sum(item["subtotal"] for item in items)
            descuento_amount = subtotal * (quotation.descuento / 100)
            subtotal_con_descuento = subtotal - descuento_amount
            impuestos = subtotal_con_descuento * 0.19  # IVA 19%
            total = subtotal_con_descuento + impuestos
            
            quotation.subtotal = subtotal
            quotation.impuestos = impuestos
            quotation.total = total
            
            created_quotations.append(quotation)
    
    db.commit()
    print(f"✓ {len(created_quotations)} cotizaciones creadas")


def create_sample_rigid_costs(db: Session):
    """Crear costos rígidos de ejemplo."""
    print("Creando costos rígidos de ejemplo...")
    
    # Obtener proyectos
    projects = db.query(Proyecto).all()
    
    rigid_costs = [
        {
            "proyecto_id": projects[0].id if projects else None,
            "nombre": "Licencia AWS",
            "descripcion": "Servicios de cloud computing Amazon Web Services",
            "tipo": TipoCosto.RECURRENTE,
            "valor": 500000,
            "moneda": "COP",
            "frecuencia": "mensual",
            "categoria": "Infraestructura",
            "proveedor": "Amazon Web Services"
        },
        {
            "proyecto_id": projects[0].id if projects else None,
            "nombre": "Licencia PostgreSQL Enterprise",
            "descripcion": "Base de datos PostgreSQL con soporte empresarial",
            "tipo": TipoCosto.FIJO,
            "valor": 2000000,
            "moneda": "COP",
            "frecuencia": "único",
            "categoria": "Software",
            "proveedor": "PostgreSQL Global Development Group"
        },
        {
            "proyecto_id": projects[1].id if len(projects) > 1 else None,
            "nombre": "Certificado SSL",
            "descripcion": "Certificado SSL para dominio de aplicación",
            "tipo": TipoCosto.FIJO,
            "valor": 150000,
            "moneda": "COP",
            "frecuencia": "anual",
            "categoria": "Seguridad",
            "proveedor": "Let's Encrypt"
        },
        {
            "nombre": "Oficina Coworking",
            "descripcion": "Espacio de trabajo compartido para el equipo",
            "tipo": TipoCosto.RECURRENTE,
            "valor": 800000,
            "moneda": "COP",
            "frecuencia": "mensual",
            "categoria": "Infraestructura",
            "proveedor": "WeWork"
        },
        {
            "nombre": "Licencias Office 365",
            "descripcion": "Suite ofimática Microsoft para el equipo",
            "tipo": TipoCosto.RECURRENTE,
            "valor": 300000,
            "moneda": "COP",
            "frecuencia": "mensual",
            "categoria": "Software",
            "proveedor": "Microsoft"
        }
    ]
    
    created_costs = []
    for cost_data in rigid_costs:
        existing_cost = db.query(CostoRigido).filter(
            CostoRigido.nombre == cost_data["nombre"]
        ).first()
        if not existing_cost:
            cost = CostoRigido(**cost_data)
            db.add(cost)
            created_costs.append(cost)
    
    db.commit()
    print(f"✓ {len(created_costs)} costos rígidos creados")


def main():
    """Función principal para inicializar datos de ejemplo."""
    print("🚀 Iniciando carga de datos de ejemplo...")
    print("=" * 50)
    
    # Crear sesión de base de datos
    db = SessionLocal()
    
    try:
        # Crear tablas si no existen
        print("Verificando tablas de base de datos...")
        import asyncio
        asyncio.run(create_tables())
        print("✓ Tablas verificadas")
        
        # Crear datos de ejemplo
        create_sample_users(db)
        create_sample_clients(db)
        create_sample_collaborators(db)
        create_sample_projects(db)
        create_sample_quotations(db)
        create_sample_rigid_costs(db)
        
        print("=" * 50)
        print("✅ Datos de ejemplo cargados exitosamente!")
        print("\nCredenciales de acceso:")
        print("- Administrador: admin@sistema.com / Admin123!")
        print("- Gerente: gerente@sistema.com / Gerente123!")
        print("- Usuario: usuario@sistema.com / Usuario123!")
        
    except Exception as e:
        print(f"❌ Error al cargar datos de ejemplo: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
