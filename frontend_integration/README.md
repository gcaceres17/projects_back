# Integración con Frontend

Esta carpeta contiene archivos de configuración y documentación para integrar el backend con aplicaciones frontend.

## Archivos Incluidos

### `FRONTEND_INTEGRATION.md`
Guía completa de integración con el frontend, incluyendo:
- Configuración de la API
- Ejemplos de código
- Mejores prácticas
- Manejo de autenticación

### `frontend-api-config.js`
Configuración lista para usar en proyectos Next.js/React:
- Cliente Axios configurado
- Interceptores para autenticación
- Funciones de API organizadas por módulo
- Manejo de errores automático

### `frontend.env.example`
Variables de entorno requeridas en el frontend:
- URL de la API
- Configuraciones de desarrollo y producción

## Uso Rápido

### Para Next.js/React

1. Copia `frontend-api-config.js` a tu proyecto como `lib/api.js`
2. Copia `frontend.env.example` a `.env.local` y configura las URLs
3. Instala las dependencias:
   ```bash
   npm install axios
   ```
4. Importa y usa:
   ```javascript
   import { authAPI, colaboradoresAPI } from '@/lib/api'
   
   // Login
   const { access_token } = await authAPI.login(email, password)
   
   // Usar API
   const colaboradores = await colaboradoresAPI.list()
   ```

## Documentación de la API

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

## Soporte

Para más información, consulta `FRONTEND_INTEGRATION.md` o la documentación de la API.
