# Sistema de Gestión de Proyectos - Backend

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791.svg?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com)

## 📋 Descripción

Sistema completo de gestión de proyectos desarrollado con **FastAPI** y **PostgreSQL**. Incluye gestión de colaboradores, proyectos, clientes, cotizaciones, costos rígidos y reportes avanzados.

## 🚀 Características

- ✅ **API REST completa** con FastAPI
- ✅ **Autenticación JWT** segura
- ✅ **Base de datos PostgreSQL** con SQLAlchemy
- ✅ **Documentación automática** con Swagger/OpenAPI
- ✅ **Containerización** con Docker
- ✅ **Migraciones** con Alembic
- ✅ **Validación de datos** con Pydantic
- ✅ **Arquitectura modular** y escalable

## 🏗️ Módulos del Sistema

### 👥 Gestión de Colaboradores
- CRUD completo de colaboradores
- Tipos: internos, externos, freelance
- Estadísticas de rendimiento
- Asignación a proyectos

### 📊 Gestión de Proyectos
- Creación y seguimiento de proyectos
- Estados: planificación, en progreso, pausado, completado
- Control de presupuestos
- Asignación de recursos

### 🏢 Gestión de Clientes
- Base de datos de clientes
- Historial de proyectos
- Estadísticas por cliente
- Información de contacto

### 💰 Sistema de Cotizaciones
- Creación de cotizaciones detalladas
- Items con precios y cantidades
- Estados: borrador, enviada, aprobada, rechazada
- Generación automática de totales

### 💸 Costos Rígidos
- Gestión de costos fijos y variables
- Categorización por tipo
- Proyecciones financieras
- Análisis por proveedor

### 📈 Sistema de Reportes
- Dashboard ejecutivo
- Reportes por período
- Estadísticas generales
- Métricas financieras

## 🛠️ Tecnologías

| Componente | Tecnología | Versión |
|------------|------------|---------|
| **Framework** | FastAPI | 0.104.1 |
| **Base de datos** | PostgreSQL | 15 |
| **ORM** | SQLAlchemy | 2.0.23 |
| **Migraciones** | Alembic | 1.13.1 |
| **Autenticación** | JWT | python-jose 3.3.0 |
| **Validación** | Pydantic | 2.5.0 |
| **Servidor** | Uvicorn | 0.24.0 |
| **Containerización** | Docker | Latest |

## 🚀 Instalación y Configuración

### Opción 1: Docker (Recomendado)

```bash
# Clonar el repositorio
git clone <repository-url>
cd projects_back

# Levantar servicios con Docker
docker-compose up -d

# Verificar que todo esté funcionando
curl http://localhost:8000/health
```

### Opción 2: Instalación Manual

```bash
# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# Ejecutar migraciones
alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --reload
```

## 🐳 Docker Services

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| **API** | 8000 | Aplicación FastAPI |
| **PostgreSQL** | 5432 | Base de datos |
| **Redis** | 6379 | Cache y sesiones |
| **pgAdmin** | 5050 | Interfaz web para PostgreSQL |

## 📖 Documentación de la API

Una vez que el servidor esté ejecutándose, puedes acceder a:

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

## 🔐 Autenticación

### Credenciales por defecto:
- **Email**: admin@sistema.com
- **Password**: admin123

### Ejemplo de uso:

```bash
# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@sistema.com", "password": "admin123"}'

# Usar token en requests
curl -X GET "http://localhost:8000/api/v1/colaboradores" \
  -H "Authorization: Bearer <your-token>"
```

## 📁 Estructura del Proyecto

```
projects_back/
├── app/                     # Aplicación principal
│   ├── main.py             # Punto de entrada
│   ├── config.py           # Configuración
│   ├── database.py         # Conexión a BD
│   ├── auth.py             # Autenticación
│   ├── models/             # Modelos SQLAlchemy
│   ├── schemas/            # Esquemas Pydantic
│   ├── routers/            # Endpoints de la API
│   └── services/           # Lógica de negocio
├── alembic/                # Migraciones de BD
├── docker/                 # Configuración Docker
├── scripts/                # Scripts de utilidad
├── tests/                  # Pruebas automatizadas
├── docker-compose.yml      # Orquestación Docker
├── Dockerfile             # Imagen de la aplicación
├── requirements.txt        # Dependencias Python
└── README.md              # Este archivo
```

## 🧪 Pruebas

```bash
# Ejecutar todas las pruebas
pytest

# Ejecutar con cobertura
pytest --cov=app

# Ejecutar pruebas específicas
pytest tests/test_auth.py -v
```

## 🔧 Configuración

### Variables de Entorno

Copia `.env.example` a `.env` y configura:

```env
# Base de datos
DATABASE_URL=postgresql://usuario:password@localhost:5432/proyecto_db

# Seguridad
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Entorno
ENVIRONMENT=development
DEBUG=true
```

## 📊 Comandos Útiles

```bash
# Ver logs de Docker
docker-compose logs -f

# Acceder al contenedor de la BD
docker-compose exec postgres psql -U usuario -d proyecto_db

# Crear nueva migración
alembic revision --autogenerate -m "descripción"

# Aplicar migraciones
alembic upgrade head

# Rollback de migración
alembic downgrade -1
```

## 🚀 Deployment

### Producción con Docker

```bash
# Construir para producción
docker-compose -f docker-compose.prod.yml up -d

# Configurar variables de entorno de producción
cp .env.example .env.prod
# Editar .env.prod con configuraciones seguras
```

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 📞 Soporte

Para soporte y consultas:
- 📧 Email: admin@sistema.com
- 📖 Documentación: http://localhost:8000/api/v1/docs

---

**Desarrollado con ❤️ usando FastAPI y PostgreSQL**
