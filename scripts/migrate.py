#!/usr/bin/env python3
"""
Script para gestionar migraciones de base de datos con Alembic.

Este script facilita la creación y aplicación de migraciones de base de datos.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Ejecutar un comando y manejar errores."""
    print(f"📋 {description}...")
    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent.parent, check=True, capture_output=True, text=True)
        print(f"✅ {description} completado")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} falló: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False

def main():
    """Función principal para gestionar migraciones."""
    if len(sys.argv) < 2:
        print("🔧 Gestor de Migraciones de Base de Datos")
        print("=" * 50)
        print("Uso: python scripts/migrate.py [comando] [opciones]")
        print()
        print("Comandos disponibles:")
        print("  init         - Inicializar Alembic (solo primera vez)")
        print("  create [msg] - Crear nueva migración")
        print("  upgrade      - Aplicar migraciones pendientes")
        print("  downgrade    - Revertir última migración")
        print("  current      - Mostrar revisión actual")
        print("  history      - Mostrar historial de migraciones")
        print("  heads        - Mostrar cabezas de migración")
        print()
        print("Ejemplos:")
        print("  python scripts/migrate.py create 'Agregar tabla usuarios'")
        print("  python scripts/migrate.py upgrade")
        print("  python scripts/migrate.py current")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    # Verificar que estamos en el directorio correcto
    current_dir = Path(__file__).parent.parent
    os.chdir(current_dir)
    
    # Verificar que existe alembic.ini
    if not (current_dir / "alembic.ini").exists():
        print("❌ Archivo alembic.ini no encontrado. Ejecuta 'init' primero.")
        sys.exit(1)
    
    print("🔧 Gestor de Migraciones de Base de Datos")
    print("=" * 50)
    
    if command == "init":
        print("🚀 Inicializando Alembic...")
        success = run_command(
            ["alembic", "init", "alembic"],
            "Inicializar Alembic"
        )
        if success:
            print("✅ Alembic inicializado. Configura alembic.ini y alembic/env.py")
    
    elif command == "create":
        message = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Auto migration"
        success = run_command(
            ["alembic", "revision", "--autogenerate", "-m", message],
            f"Crear migración: {message}"
        )
        if success:
            print("✅ Migración creada. Revisa el archivo generado antes de aplicar.")
    
    elif command == "upgrade":
        target = sys.argv[2] if len(sys.argv) > 2 else "head"
        success = run_command(
            ["alembic", "upgrade", target],
            f"Aplicar migraciones hasta: {target}"
        )
        if success:
            print("✅ Migraciones aplicadas exitosamente.")
    
    elif command == "downgrade":
        target = sys.argv[2] if len(sys.argv) > 2 else "-1"
        success = run_command(
            ["alembic", "downgrade", target],
            f"Revertir migraciones hasta: {target}"
        )
        if success:
            print("✅ Migraciones revertidas exitosamente.")
    
    elif command == "current":
        success = run_command(
            ["alembic", "current"],
            "Mostrar revisión actual"
        )
    
    elif command == "history":
        success = run_command(
            ["alembic", "history"],
            "Mostrar historial de migraciones"
        )
    
    elif command == "heads":
        success = run_command(
            ["alembic", "heads"],
            "Mostrar cabezas de migración"
        )
    
    elif command == "reset":
        print("⚠️  ADVERTENCIA: Esto eliminará todas las migraciones y recreará la base de datos")
        confirm = input("¿Estás seguro? (escriba 'SI' para confirmar): ")
        if confirm == "SI":
            # Eliminar todas las migraciones
            versions_dir = current_dir / "alembic" / "versions"
            if versions_dir.exists():
                for migration_file in versions_dir.glob("*.py"):
                    if migration_file.name != "__init__.py":
                        migration_file.unlink()
                        print(f"🗑️  Eliminada: {migration_file.name}")
            
            # Crear nueva migración inicial
            success = run_command(
                ["alembic", "revision", "--autogenerate", "-m", "Initial migration"],
                "Crear migración inicial"
            )
            if success:
                print("✅ Base de datos reseteada. Aplica la migración inicial con 'upgrade'.")
        else:
            print("❌ Operación cancelada.")
    
    else:
        print(f"❌ Comando desconocido: {command}")
        print("Usa 'python scripts/migrate.py' para ver la ayuda.")
        sys.exit(1)


if __name__ == "__main__":
    main()
