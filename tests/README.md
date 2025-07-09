# Tests Directory

Esta carpeta contiene las pruebas automatizadas del sistema.

## Estructura

```
tests/
├── __init__.py              # Archivo de inicialización
├── conftest.py              # Configuración de pytest
├── test_auth.py             # Pruebas de autenticación
├── test_colaboradores.py    # Pruebas de colaboradores
├── test_proyectos.py        # Pruebas de proyectos
├── test_clientes.py         # Pruebas de clientes
├── test_cotizaciones.py     # Pruebas de cotizaciones
├── test_costos_rigidos.py   # Pruebas de costos rígidos
└── test_reportes.py         # Pruebas de reportes
```

## Ejecutar Pruebas

```bash
# Ejecutar todas las pruebas
pytest

# Ejecutar con cobertura
pytest --cov=app

# Ejecutar pruebas específicas
pytest tests/test_auth.py
```
