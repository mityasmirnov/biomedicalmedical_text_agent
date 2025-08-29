import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const api = {
  // Dashboard APIs
  dashboard: {
    getSystemStatus: () => apiClient.get('/dashboard/system-status'),
    getProcessingQueue: () => apiClient.get('/dashboard/recent-activities'),
    getRecentResults: () => apiClient.get('/dashboard/statistics'),
  },

  // Metadata APIs
  metadata: {
    search: (params: any) => apiClient.get('/metadata/search', { params }),
    export: (params: any) => apiClient.post('/metadata/download-document', params),
    getAll: () => apiClient.get('/metadata'),
    getById: (id: string) => apiClient.get(`/metadata/${id}`),
  },

  // Document APIs
  documents: {
    getAll: () => apiClient.get('/documents'),
    getById: (id: string) => apiClient.get(`/documents/${id}`),
    upload: (formData: FormData) => apiClient.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),
    startExtraction: (id: string, params: any) => apiClient.post(`/documents/${id}/extract`, params),
    getExtractionResults: (id: string) => apiClient.get(`/documents/${id}/full-text`),
    extract: (id: string) => apiClient.post(`/documents/${id}/extract`),
    delete: (id: string) => apiClient.delete(`/documents/${id}`),
  },

  // Validation APIs
  validation: {
    getExtractionData: (id: string) => apiClient.get(`/validation/${id}`),
    submitValidation: (id: string, data: any) => apiClient.post(`/validation/${id}/submit`, data),
    getQueue: (status?: string) => apiClient.get('/validation/queue', { params: { status } }),
  },

  // Database APIs
  database: {
    getTables: () => apiClient.get('/database/status'),
    getTableData: (table: string, params?: any) => apiClient.get(`/database/${table}`, { params }),
    getTableSchema: (table: string) => apiClient.get(`/database/${table}/schema`),
    getStatistics: () => apiClient.get('/database/status'),
    exportTable: (table: string) => apiClient.get(`/database/${table}/export`),
    query: (sql: string) => apiClient.post('/database/query', { sql }),
  },

  // Agents APIs
  agents: {
    getAll: () => apiClient.get('/agents'),
    getById: (id: string) => apiClient.get(`/agents/${id}`),
    start: (id: string) => apiClient.post(`/agents/${id}/start`),
    stop: (id: string) => apiClient.post(`/agents/${id}/stop`),
  },

  // Configuration APIs
  config: {
    getProviders: () => apiClient.get('/config/providers'),
    updateProvider: (provider: string, data: any) => apiClient.put(`/config/providers/${provider}`, data),
    getModels: () => apiClient.get('/config/models'),
    updateApiKey: (provider: string, apiKey: string) => apiClient.put(`/config/providers/${provider}/key`, { api_key: apiKey }),
    getUsage: () => apiClient.get('/config/usage'),
  },

  // Ontology APIs
  ontologies: {
    getAll: () => apiClient.get('/ontologies'),
    getTerms: (ontologyId: string) => apiClient.get(`/ontologies/${ontologyId}/terms`),
    getTermDetails: (termId: string) => apiClient.get(`/ontologies/terms/${termId}`),
    search: (params: any) => apiClient.post('/ontologies/search', params),
    updateTerm: (termId: string, data: any) => apiClient.put(`/ontologies/terms/${termId}`, data),
  },

  // Prompt APIs
  prompts: {
    getAll: () => apiClient.get('/prompts'),
    getById: (id: string) => apiClient.get(`/prompts/${id}`),
    create: (data: any) => apiClient.post('/prompts', data),
    update: (id: string, data: any) => apiClient.put(`/prompts/${id}`, data),
    delete: (id: string) => apiClient.delete(`/prompts/${id}`),
    getLangExtractInstructions: () => apiClient.get('/prompts/langextract-instructions'),
    createLangExtractInstruction: (data: any) => apiClient.post('/prompts/langextract-instructions', data),
    updateLangExtractInstruction: (id: string, data: any) => apiClient.put(`/prompts/langextract-instructions/${id}`, data),
    test: (id: string, data: any) => apiClient.post(`/prompts/${id}/test`, data),
  },

  // Analytics APIs
  analytics: {
    getVisualizations: (params: any) => apiClient.get('/analytics/visualizations', { params }),
    exportVisualizations: (params: any) => apiClient.post('/analytics/export', params),
    getMetrics: () => apiClient.get('/analytics/metrics'),
  },

  // Authentication APIs
  auth: {
    login: (credentials: any) => apiClient.post('/auth/login', credentials),
    logout: () => apiClient.post('/auth/logout'),
    refresh: () => apiClient.post('/auth/refresh'),
    getProfile: () => apiClient.get('/auth/profile'),
  },
};

export default apiClient;
