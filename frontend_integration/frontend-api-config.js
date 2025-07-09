// API Configuration for Next.js Frontend
// Place this in: lib/api.js

import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 seconds timeout
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      // Try to refresh token
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${api.defaults.baseURL}/auth/refresh`, {
            refresh_token: refreshToken
          });
          
          const { access_token } = response.data;
          localStorage.setItem('access_token', access_token);
          
          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

export default api;

// Auth API functions
export const authAPI = {
  login: async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },
  
  register: async (userData) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },
  
  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
  
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }
};

// Colaboradores API functions
export const colaboradoresAPI = {
  list: async (params = {}) => {
    const response = await api.get('/colaboradores', { params });
    return response.data;
  },
  
  create: async (data) => {
    const response = await api.post('/colaboradores', data);
    return response.data;
  },
  
  getById: async (id) => {
    const response = await api.get(`/colaboradores/${id}`);
    return response.data;
  },
  
  update: async (id, data) => {
    const response = await api.put(`/colaboradores/${id}`, data);
    return response.data;
  },
  
  delete: async (id) => {
    const response = await api.delete(`/colaboradores/${id}`);
    return response.data;
  },
  
  getStatistics: async (id) => {
    const response = await api.get(`/colaboradores/${id}/estadisticas`);
    return response.data;
  }
};

// Proyectos API functions
export const proyectosAPI = {
  list: async (params = {}) => {
    const response = await api.get('/proyectos', { params });
    return response.data;
  },
  
  create: async (data) => {
    const response = await api.post('/proyectos', data);
    return response.data;
  },
  
  getById: async (id) => {
    const response = await api.get(`/proyectos/${id}`);
    return response.data;
  },
  
  update: async (id, data) => {
    const response = await api.put(`/proyectos/${id}`, data);
    return response.data;
  },
  
  delete: async (id) => {
    const response = await api.delete(`/proyectos/${id}`);
    return response.data;
  },
  
  getStatistics: async (id) => {
    const response = await api.get(`/proyectos/${id}/estadisticas`);
    return response.data;
  }
};

// Clientes API functions
export const clientesAPI = {
  list: async (params = {}) => {
    const response = await api.get('/clientes', { params });
    return response.data;
  },
  
  create: async (data) => {
    const response = await api.post('/clientes', data);
    return response.data;
  },
  
  getById: async (id) => {
    const response = await api.get(`/clientes/${id}`);
    return response.data;
  },
  
  update: async (id, data) => {
    const response = await api.put(`/clientes/${id}`, data);
    return response.data;
  },
  
  delete: async (id) => {
    const response = await api.delete(`/clientes/${id}`);
    return response.data;
  },
  
  getProjects: async (id) => {
    const response = await api.get(`/clientes/${id}/proyectos`);
    return response.data;
  },
  
  getStatistics: async (id) => {
    const response = await api.get(`/clientes/${id}/estadisticas`);
    return response.data;
  }
};

// Cotizaciones API functions
export const cotizacionesAPI = {
  list: async (params = {}) => {
    const response = await api.get('/cotizaciones', { params });
    return response.data;
  },
  
  create: async (data) => {
    const response = await api.post('/cotizaciones', data);
    return response.data;
  },
  
  getById: async (id) => {
    const response = await api.get(`/cotizaciones/${id}`);
    return response.data;
  },
  
  update: async (id, data) => {
    const response = await api.put(`/cotizaciones/${id}`, data);
    return response.data;
  },
  
  delete: async (id) => {
    const response = await api.delete(`/cotizaciones/${id}`);
    return response.data;
  },
  
  approve: async (id) => {
    const response = await api.post(`/cotizaciones/${id}/aprobar`);
    return response.data;
  },
  
  reject: async (id, reason) => {
    const response = await api.post(`/cotizaciones/${id}/rechazar`, { reason });
    return response.data;
  }
};

// Costos Rígidos API functions
export const costosRigidosAPI = {
  list: async (params = {}) => {
    const response = await api.get('/costos-rigidos', { params });
    return response.data;
  },
  
  create: async (data) => {
    const response = await api.post('/costos-rigidos', data);
    return response.data;
  },
  
  getById: async (id) => {
    const response = await api.get(`/costos-rigidos/${id}`);
    return response.data;
  },
  
  update: async (id, data) => {
    const response = await api.put(`/costos-rigidos/${id}`, data);
    return response.data;
  },
  
  delete: async (id) => {
    const response = await api.delete(`/costos-rigidos/${id}`);
    return response.data;
  },
  
  getStatistics: async () => {
    const response = await api.get('/costos-rigidos/estadisticas/resumen');
    return response.data;
  },
  
  getCategories: async () => {
    const response = await api.get('/costos-rigidos/categorias/lista');
    return response.data;
  },
  
  getProviders: async () => {
    const response = await api.get('/costos-rigidos/proveedores/lista');
    return response.data;
  },
  
  getProjection: async (params = {}) => {
    const response = await api.get('/costos-rigidos/calcular-proyeccion', { params });
    return response.data;
  }
};

// Reportes API functions
export const reportesAPI = {
  getDashboard: async () => {
    const response = await api.get('/reportes/dashboard');
    return response.data;
  },
  
  getProjectsByStatus: async () => {
    const response = await api.get('/reportes/proyectos-por-estado');
    return response.data;
  },
  
  getQuotationsByMonth: async (year) => {
    const response = await api.get(`/reportes/cotizaciones-por-mes?año=${year}`);
    return response.data;
  },
  
  getRigidCostsSummary: async () => {
    const response = await api.get('/reportes/costos-rigidos-resumen');
    return response.data;
  },
  
  getCollaboratorsProductivity: async () => {
    const response = await api.get('/reportes/colaboradores-productividad');
    return response.data;
  },
  
  getMostActiveClients: async (limit = 10) => {
    const response = await api.get(`/reportes/clientes-mas-activos?limite=${limit}`);
    return response.data;
  },
  
  getFinancialSummary: async () => {
    const response = await api.get('/reportes/resumen-financiero');
    return response.data;
  }
};

// Utility functions
export const apiUtils = {
  // Check if API is available
  healthCheck: async () => {
    try {
      const response = await axios.get(`${api.defaults.baseURL.replace('/api/v1', '')}/health`);
      return response.data;
    } catch (error) {
      throw new Error('API is not available');
    }
  },
  
  // Handle API errors
  handleError: (error) => {
    if (error.response) {
      // Server responded with error status
      return {
        message: error.response.data.detail || 'Error en el servidor',
        status: error.response.status
      };
    } else if (error.request) {
      // Request was made but no response received
      return {
        message: 'No se pudo conectar con el servidor',
        status: 0
      };
    } else {
      // Something else happened
      return {
        message: error.message || 'Error desconocido',
        status: 0
      };
    }
  }
};
