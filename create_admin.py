#!/usr/bin/env python3
"""
Script para crear usuario administrador
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

def create_admin_user():
    """Crear usuario administrador"""
    db = SessionLocal()
    
    try:
        # Verificar si ya existe el usuario admin
        existing_admin = db.query(User).filter(User.email == "admin@example.com").first()
        
        if existing_admin:
            print("✅ Usuario admin ya existe")
            print(f"   Email: {existing_admin.email}")
            print(f"   Activo: {existing_admin.is_active}")
            print(f"   Admin: {existing_admin.is_admin}")
            return
        
        # Crear nuevo usuario admin
        hashed_password = get_password_hash("admin123")
        admin_user = User(
            email="admin@example.com",
            nombre="Administrador",
            hashed_password=hashed_password,
            is_active=True,
            is_admin=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ Usuario admin creado exitosamente!")
        print(f"   Email: {admin_user.email}")
        print(f"   Password: admin123")
        print(f"   ID: {admin_user.id}")
        
    except Exception as e:
        print(f"❌ Error al crear usuario admin: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
