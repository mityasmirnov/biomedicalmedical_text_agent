import axios from 'axios';

// --- Axios Instance ---
const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL || '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// --- Interceptors ---
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers = config.headers || {};
      (config.headers as any)['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// --- API Definitions ---

// Auth API
export const authAPI = {
  login: async (credentials: any) => {
    const response = await apiClient.post('/auth/token', new URLSearchParams(credentials), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    // After login, fetch user data
    const userResponse = await authAPI.verifyToken(response.data.access_token);
    return { token: response.data.access_token, user: userResponse.user };
  },
  register: async (userData: any) => {
    const response = await apiClient.post('/auth/register', userData);
    const userResponse = await authAPI.verifyToken(response.data.access_token);
    return { token: response.data.access_token, user: userResponse.user };
  },
  logout: () => apiClient.post('/auth/logout'),
  verifyToken: async (token: string) => {
    const response = await apiClient.post('/auth/verify', null, {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    return response.data;
  },
  refreshToken: async (token: string) => {
    const response = await apiClient.post('/auth/refresh', null, {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    const userResponse = await authAPI.verifyToken(response.data.access_token);
    return { token: response.data.access_token, user: userResponse.user };
  },
};

// Dashboard API
export const dashboardAPI = {
  getOverview: () => apiClient.get('/dashboard/overview'),
  getStatistics: () => apiClient.get('/dashboard/statistics'),
  getSystemStatus: () => apiClient.get('/dashboard/system-status'),
  getRecentActivities: () => apiClient.get('/dashboard/recent-activities'),
  getAlerts: () => apiClient.get('/dashboard/alerts'),
};

// Agents API
export const agentsAPI = {
  getAgents: () => apiClient.get('/agents/'),
  getAgent: (id: string) => apiClient.get(`/agents/${id}/`),
  startAgent: (id: string) => apiClient.post(`/agents/${id}/start/`),
  stopAgent: (id: string) => apiClient.post(`/agents/${id}/stop/`),
};

// Documents API
export const documentsAPI = {
  getDocuments: () => apiClient.get('/documents/'),
  getDocument: (id: string) => apiClient.get(`/documents/${id}/`),
  getDocumentFullText: (id: string) => apiClient.get(`/documents/${id}/full-text/`),
};

// Metadata API
export const metadataAPI = {
  getMetadataOverview: () => apiClient.get('/metadata/'),
  getCollection: (name: string) => apiClient.get(`/metadata/collections/${name}/`),
  getCollectionDocuments: (name: string, limit = 100, offset = 0) => 
    apiClient.get(`/metadata/collections/${name}/documents/?limit=${limit}&offset=${offset}`),
  searchMetadata: (query: string, collection?: string, limit = 100) => 
    apiClient.get(`/metadata/search/?query=${query}&collection=${collection || ''}&limit=${limit}`),
};

export default apiClient;
