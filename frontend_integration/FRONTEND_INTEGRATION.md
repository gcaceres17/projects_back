# API Configuration for Frontend Integration

## Backend Configuration

### API Base URL
```
Development: http://localhost:8000/api/v1
Production: https://your-domain.com/api/v1
```

### CORS Configuration
The backend is configured to accept requests from:
- http://localhost:3000 (Next.js default port)
- http://localhost:3001 (Alternative port)

## API Endpoints

### Authentication
- POST `/auth/login` - Login user
- POST `/auth/register` - Register new user
- POST `/auth/refresh` - Refresh token
- GET `/auth/me` - Get current user

### Colaboradores
- GET `/colaboradores` - List collaborators with pagination
- POST `/colaboradores` - Create new collaborator
- GET `/colaboradores/{id}` - Get collaborator by ID
- PUT `/colaboradores/{id}` - Update collaborator
- DELETE `/colaboradores/{id}` - Delete collaborator
- GET `/colaboradores/{id}/estadisticas` - Get collaborator statistics

### Proyectos
- GET `/proyectos` - List projects with pagination
- POST `/proyectos` - Create new project
- GET `/proyectos/{id}` - Get project by ID
- PUT `/proyectos/{id}` - Update project
- DELETE `/proyectos/{id}` - Delete project
- GET `/proyectos/{id}/estadisticas` - Get project statistics

### Clientes
- GET `/clientes` - List clients with pagination
- POST `/clientes` - Create new client
- GET `/clientes/{id}` - Get client by ID
- PUT `/clientes/{id}` - Update client
- DELETE `/clientes/{id}` - Delete client
- GET `/clientes/{id}/proyectos` - Get client projects
- GET `/clientes/{id}/estadisticas` - Get client statistics

### Cotizaciones
- GET `/cotizaciones` - List quotations with pagination
- POST `/cotizaciones` - Create new quotation
- GET `/cotizaciones/{id}` - Get quotation by ID
- PUT `/cotizaciones/{id}` - Update quotation
- DELETE `/cotizaciones/{id}` - Delete quotation
- POST `/cotizaciones/{id}/aprobar` - Approve quotation
- POST `/cotizaciones/{id}/rechazar` - Reject quotation

### Costos Rígidos
- GET `/costos-rigidos` - List rigid costs with pagination
- POST `/costos-rigidos` - Create new rigid cost
- GET `/costos-rigidos/{id}` - Get rigid cost by ID
- PUT `/costos-rigidos/{id}` - Update rigid cost
- DELETE `/costos-rigidos/{id}` - Delete rigid cost
- GET `/costos-rigidos/estadisticas/resumen` - Get cost statistics
- GET `/costos-rigidos/categorias/lista` - Get cost categories
- GET `/costos-rigidos/proveedores/lista` - Get providers list

### Reportes
- GET `/reportes/dashboard` - Dashboard statistics
- GET `/reportes/proyectos-por-estado` - Projects by status
- GET `/reportes/cotizaciones-por-mes` - Quotations by month
- GET `/reportes/costos-rigidos-resumen` - Rigid costs summary
- GET `/reportes/colaboradores-productividad` - Collaborators productivity
- GET `/reportes/clientes-mas-activos` - Most active clients
- GET `/reportes/resumen-financiero` - Financial summary

## Authentication

### Headers Required
```
Authorization: Bearer {token}
Content-Type: application/json
```

### Login Response
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "email": "admin@sistema.com",
    "nombre": "Admin",
    "is_active": true,
    "is_admin": true
  }
}
```

## Data Models

### Pagination Response
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "size": 10,
  "pages": 10,
  "has_next": true,
  "has_previous": false
}
```

### Error Response
```json
{
  "detail": "Error message"
}
```

## Frontend Integration Steps

1. **Install HTTP Client**
   ```bash
   npm install axios
   # or
   npm install @tanstack/react-query
   ```

2. **Configure API Base URL**
   ```javascript
   // lib/api.js
   import axios from 'axios';
   
   const api = axios.create({
     baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
     headers: {
       'Content-Type': 'application/json',
     },
   });
   
   // Add token to requests
   api.interceptors.request.use((config) => {
     const token = localStorage.getItem('access_token');
     if (token) {
       config.headers.Authorization = `Bearer ${token}`;
     }
     return config;
   });
   ```

3. **Environment Variables**
   ```env
   # .env.local
   NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
   ```

4. **Example API Calls**
   ```javascript
   // services/colaboradores.js
   import api from '../lib/api';
   
   export const getColaboradores = async (page = 1, limit = 10) => {
     const response = await api.get(`/colaboradores?skip=${(page-1)*limit}&limit=${limit}`);
     return response.data;
   };
   
   export const createColaborador = async (data) => {
     const response = await api.post('/colaboradores', data);
     return response.data;
   };
   ```

## Testing

### Start Backend Server
```bash
cd projects_back
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Start Frontend Server
```bash
cd projects_front
npm run dev
```

### Test API Connection
```bash
curl -X GET "http://localhost:8000/health"
```

## Notes

- All endpoints require authentication except `/health` and `/auth/login`
- Use pagination for list endpoints
- Handle errors appropriately in the frontend
- Implement token refresh logic
- Use environment variables for configuration
