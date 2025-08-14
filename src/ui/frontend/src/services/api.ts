import axios from 'axios';

// --- Axios Instance ---
const apiClient = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// --- Interceptors ---
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
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

export default apiClient;
