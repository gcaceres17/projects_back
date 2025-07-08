# Sistema de Gestión de Proyectos - Backend API

## Descripción

API REST desarrollada con FastAPI para un sistema integral de gestión de proyectos. Proporciona endpoints para gestionar colaboradores, proyectos, cotizaciones, costos y generar reportes analíticos.

## ✨ Características Principales

- **🔐 Autenticación JWT** - Sistema de autenticación seguro con tokens JWT
- **🐘 Base de Datos PostgreSQL** - Almacenamiento robusto y escalable
- **✅ Validación de Datos** - Validación automática con Pydantic
- **📚 Documentación Automática** - API docs con Swagger UI y ReDoc
- **🔄 Migraciones de Base de Datos** - Gestión de esquemas con Alembic
- **📝 Logging Completo** - Sistema de logs para monitoreo y debugging
- **🛡️ Manejo de Errores** - Gestión robusta de errores y excepciones
- **🌐 CORS Configurado** - Soporte para aplicaciones frontend

## 🎯 Módulos Principales

### 🧑‍💼 Gestión de Colaboradores
- CRUD completo de colaboradores
- Clasificación por tipo (interno, externo, freelance)
- Gestión de habilidades y disponibilidad
- Seguimiento de costos por hora
- Estadísticas y métricas

### 📋 Gestión de Proyectos
- Creación y seguimiento de proyectos
- Asignación de colaboradores
- Control de presupuestos y costos
- Seguimiento de progreso y tiempos
- Estados de proyecto (planificación, en progreso, completado, etc.)

### 💰 Gestión de Cotizaciones
- Creación de cotizaciones detalladas
- Seguimiento de estados (borrador, enviada, aprobada, etc.)
- Cálculo automático de totales e impuestos
- Items de cotización con cantidades y precios
- Generación de reportes

### 💸 Costos Rígidos
- Gestión de costos fijos y variables
- Categorización de gastos
- Asociación con proyectos específicos
- Seguimiento de proveedores
- Frecuencias de pago

### 📊 Reportes y Analíticas
- Dashboards con métricas clave
- Reportes financieros
- Análisis de rendimiento
- Exportación en múltiples formatos

## 🗂️ Estructura del Proyecto

```
projects_back/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicación principal FastAPI
│   ├── config.py            # Configuración de la aplicación
│   ├── database.py          # Configuración de base de datos
│   ├── auth.py              # Autenticación y seguridad
│   ├── models/              # Modelos SQLAlchemy
│   │   └── __init__.py
│   ├── schemas/             # Esquemas Pydantic
│   │   ├── __init__.py
│   │   ├── colaborador.py
│   │   ├── proyecto.py
│   │   ├── cliente.py
│   │   ├── cotizacion.py
│   │   ├── costo_rigido.py
│   │   ├── usuario.py
│   │   └── reporte.py
│   ├── routers/             # Endpoints de la API
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── colaboradores.py
│   │   ├── proyectos.py
│   │   ├── clientes.py
│   │   ├── cotizaciones.py
│   │   └── costos_rigidos.py
│   ├── services/            # Lógica de negocio
│   │   ├── colaborador_service.py
│   │   ├── proyecto_service.py
│   │   └── cotizacion_service.py
│   └── utils/               # Utilidades y helpers
├── alembic/                 # Migraciones de base de datos
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── scripts/                 # Scripts de utilidad
│   ├── init_sample_data.py  # Cargar datos de ejemplo
│   ├── run_dev.py          # Servidor de desarrollo
│   ├── migrate.py          # Gestión de migraciones
│   └── setup_dev.py        # Configuración automática
├── tests/                   # Pruebas automatizadas
├── .env.example            # Ejemplo de variables de entorno
├── .gitignore
├── alembic.ini             # Configuración de Alembic
├── requirements.txt        # Dependencias de Python
└── README.md
```

## 🚀 Instalación y Configuración

### Prerrequisitos

- Python 3.8 o superior
- PostgreSQL 12 o superior
- Git

### 🔧 Instalación Rápida

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd projects_back
```

2. **Crear y activar entorno virtual**
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tu configuración
```

5. **Configurar base de datos**
```bash
# Crear base de datos PostgreSQL
createdb proyecto_db

# Ejecutar migraciones
python scripts/migrate.py create "Initial migration"
python scripts/migrate.py upgrade
```

6. **Cargar datos de ejemplo (opcional)**
```bash
python scripts/init_sample_data.py
```

7. **Iniciar servidor de desarrollo**
```bash
python scripts/run_dev.py
```

### ⚡ Configuración Automática

Para una configuración automatizada, ejecuta:

```bash
python scripts/setup_dev.py
```

Este script realizará toda la configuración inicial automáticamente.

## 🎮 Uso

### Iniciar el Servidor

```bash
# Desarrollo
python scripts/run_dev.py

# Producción
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Acceder a la API

- **API Base**: http://localhost:8000
- **Documentación Swagger**: http://localhost:8000/api/v1/docs
- **Documentación ReDoc**: http://localhost:8000/api/v1/redoc
- **Health Check**: http://localhost:8000/health

### 🔑 Credenciales por Defecto

- **Administrador**: admin@sistema.com / Admin123!
- **Gerente**: gerente@sistema.com / Gerente123!
- **Usuario**: usuario@sistema.com / Usuario123!

## 🗄️ Gestión de Base de Datos

### Migraciones

```bash
# Crear nueva migración
python scripts/migrate.py create "Descripción del cambio"

# Aplicar migraciones
python scripts/migrate.py upgrade

# Revertir migración
python scripts/migrate.py downgrade

# Ver estado actual
python scripts/migrate.py current

# Ver historial
python scripts/migrate.py history

# Resetear base de datos
python scripts/migrate.py reset
```

### Datos de Ejemplo

```bash
# Cargar datos de ejemplo
python scripts/init_sample_data.py
```

## 🔗 Endpoints Principales

### 🔐 Autenticación
- `POST /api/v1/auth/login` - Iniciar sesión
- `POST /api/v1/auth/register` - Registrar usuario
- `GET /api/v1/auth/me` - Información del usuario actual
- `POST /api/v1/auth/change-password` - Cambiar contraseña
- `POST /api/v1/auth/logout` - Cerrar sesión

### 🧑‍💼 Colaboradores
- `GET /api/v1/colaboradores` - Listar colaboradores
- `POST /api/v1/colaboradores` - Crear colaborador
- `GET /api/v1/colaboradores/{id}` - Obtener colaborador
- `PUT /api/v1/colaboradores/{id}` - Actualizar colaborador
- `DELETE /api/v1/colaboradores/{id}` - Eliminar colaborador
- `GET /api/v1/colaboradores/disponibles` - Colaboradores disponibles
- `GET /api/v1/colaboradores/estadisticas` - Estadísticas de colaboradores

### 📋 Proyectos
- `GET /api/v1/proyectos` - Listar proyectos
- `POST /api/v1/proyectos` - Crear proyecto
- `GET /api/v1/proyectos/{id}` - Obtener proyecto
- `PUT /api/v1/proyectos/{id}` - Actualizar proyecto
- `DELETE /api/v1/proyectos/{id}` - Eliminar proyecto
- `POST /api/v1/proyectos/{id}/asignar-colaborador` - Asignar colaborador
- `DELETE /api/v1/proyectos/{id}/desasignar-colaborador/{colaborador_id}` - Desasignar colaborador
- `PATCH /api/v1/proyectos/{id}/progreso` - Actualizar progreso
- `GET /api/v1/proyectos/estadisticas` - Estadísticas de proyectos

### 💰 Cotizaciones
- `GET /api/v1/cotizaciones` - Listar cotizaciones
- `POST /api/v1/cotizaciones` - Crear cotización
- `GET /api/v1/cotizaciones/{id}` - Obtener cotización
- `PUT /api/v1/cotizaciones/{id}` - Actualizar cotización
- `DELETE /api/v1/cotizaciones/{id}` - Eliminar cotización
- `POST /api/v1/cotizaciones/{id}/enviar` - Enviar cotización
- `GET /api/v1/cotizaciones/estadisticas` - Estadísticas de cotizaciones

### 💸 Costos Rígidos
- `GET /api/v1/costos-rigidos` - Listar costos
- `POST /api/v1/costos-rigidos` - Crear costo
- `GET /api/v1/costos-rigidos/{id}` - Obtener costo
- `PUT /api/v1/costos-rigidos/{id}` - Actualizar costo
- `DELETE /api/v1/costos-rigidos/{id}` - Eliminar costo
- `GET /api/v1/costos-rigidos/estadisticas` - Estadísticas de costos

## ⚙️ Variables de Entorno

```bash
# Base de datos
DATABASE_URL=postgresql://usuario:password@localhost/proyecto_db
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=proyecto_db
DATABASE_USER=usuario
DATABASE_PASSWORD=password

# Seguridad
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Aplicación
ENVIRONMENT=development
DEBUG=true
API_V1_STR=/api/v1
PROJECT_NAME=Sistema de Gestión de Proyectos
PROJECT_VERSION=1.0.0

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:3001"]

# Email (opcional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=tu-password
EMAILS_FROM_EMAIL=tu-email@gmail.com
EMAILS_FROM_NAME=Sistema de Gestión de Proyectos
```

## 🧪 Pruebas

```bash
# Ejecutar todas las pruebas
pytest

# Ejecutar con coverage
pytest --cov=app

# Ejecutar pruebas específicas
pytest tests/test_colaboradores.py

# Ejecutar pruebas en modo verboso
pytest -v
```

## 📦 Despliegue

### Docker

```bash
# Construir imagen
docker build -t sistema-proyectos-api .

# Ejecutar contenedor
docker run -p 8000:8000 sistema-proyectos-api
```

### Producción

1. **Configurar variables de entorno de producción**
2. **Aplicar migraciones**: `python scripts/migrate.py upgrade`
3. **Configurar servidor web** (Nginx/Apache)
4. **Configurar SSL/TLS**
5. **Configurar monitoreo y logs**
6. **Configurar backup de base de datos**

## 📊 Monitoreo y Logs

Los logs se guardan en:
- **Archivo**: `app.log`
- **Consola**: Salida estándar
- **Nivel**: INFO en producción, DEBUG en desarrollo

### Estructura de Logs

```
YYYY-MM-DD HH:MM:SS - logger_name - LEVEL - message
```

## 🤝 Contribución

1. Fork el repositorio
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🛠️ Desarrollo

### Estándares de Código

- **PEP 8**: Seguir estándares de estilo Python
- **Type Hints**: Usar anotaciones de tipo
- **Docstrings**: Documentar funciones y clases
- **Tests**: Escribir pruebas para nuevas funcionalidades

### Herramientas de Desarrollo

- **Black**: Formateo de código
- **isort**: Ordenamiento de imports
- **flake8**: Linting
- **mypy**: Verificación de tipos
- **pytest**: Framework de pruebas

## 🆘 Soporte

Para soporte técnico o preguntas:
- **Email**: admin@sistema.com
- **Issues**: GitHub Issues
- **Documentación**: `/docs` endpoint

## 🎯 Próximas Características

- [ ] Módulo de reportes avanzados
- [ ] Integración con servicios de email
- [ ] API de notificaciones push
- [ ] Dashboard en tiempo real
- [ ] Integración con sistemas de pago
- [ ] Módulo de inventario
- [ ] Sistema de workflows
- [ ] Integración con calendarios

---

**Desarrollado con ❤️ usando FastAPI y PostgreSQL**

4. **Run the application**:
```bash
uvicorn main:app --reload
```

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
projects_back/
├── app/
│   ├── models/         # SQLAlchemy models
│   ├── schemas/        # Pydantic schemas
│   ├── routers/        # API route handlers
│   ├── services/       # Business logic
│   ├── database.py     # Database configuration
│   ├── auth.py         # Authentication utilities
│   └── config.py       # Application settings
├── alembic/           # Database migrations
├── tests/             # Test files
├── requirements.txt   # Python dependencies
└── main.py           # Application entry point
```

## Development

- **Add migration**: `alembic revision --autogenerate -m "description"`
- **Apply migrations**: `alembic upgrade head`
- **Run tests**: `pytest`
- **Format code**: `black .`
- **Lint code**: `flake8`

## Deployment

The application is ready for deployment on platforms like:
- **Heroku**
- **Railway**
- **DigitalOcean App Platform**
- **AWS EC2/ECS**
- **Google Cloud Run**
