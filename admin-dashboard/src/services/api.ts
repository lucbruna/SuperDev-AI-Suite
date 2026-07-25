import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000,
    });

    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    this.client.interceptors.response.use(
      (response: AxiosResponse) => response,
      async (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('access_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  async get<T>(url: string, config?: AxiosRequestConfig) {
    return this.client.get<T>(url, config);
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig) {
    return this.client.post<T>(url, data, config);
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig) {
    return this.client.put<T>(url, data, config);
  }

  async patch<T>(url: string, data?: any, config?: AxiosRequestConfig) {
    return this.client.patch<T>(url, data, config);
  }

  async delete<T>(url: string, config?: AxiosRequestConfig) {
    return this.client.delete<T>(url, config);
  }
}

export const api = new ApiService();

// Health
export const healthCheck = () => api.get('/health');
export const getVersion = () => api.get('/version');

// Auth
export const authApi = {
  login: (email: string, password: string) => api.post('/auth/login', { email, password }),
  register: (data: any) => api.post('/auth/register', data),
  logout: () => api.post('/auth/logout'),
  me: () => api.get('/auth/me'),
  refresh: () => api.post('/auth/refresh'),
};

// Organizations
export const organizationsApi = {
  list: () => api.get('/organizations'),
  get: (id: string) => api.get(`/organizations/${id}`),
  create: (data: any) => api.post('/organizations', data),
  update: (id: string, data: any) => api.put(`/organizations/${id}`, data),
  delete: (id: string) => api.delete(`/organizations/${id}`),
  members: (id: string) => api.get(`/organizations/${id}/members`),
  invite: (id: string, data: any) => api.post(`/organizations/${id}/invite`, data),
  removeMember: (id: string, userId: string) => api.delete(`/organizations/${id}/members/${userId}`),
  updateMember: (id: string, userId: string, data: any) => api.put(`/organizations/${id}/members/${userId}`, data),
};

// Projects
export const projectsApi = {
  list: (orgId: string) => api.get(`/organizations/${orgId}/projects`),
  get: (id: string) => api.get(`/projects/${id}`),
  create: (orgId: string, data: any) => api.post(`/organizations/${orgId}/projects`, data),
  update: (id: string, data: any) => api.put(`/projects/${id}`, data),
  delete: (id: string) => api.delete(`/projects/${id}`),
  members: (id: string) => api.get(`/projects/${id}/members`),
  invite: (id: string, data: any) => api.post(`/projects/${id}/invite`, data),
};

// Workflows
export const workflowsApi = {
  list: (projectId: string) => api.get(`/projects/${projectId}/workflows`),
  get: (id: string) => api.get(`/workflows/${id}`),
  create: (projectId: string, data: any) => api.post(`/projects/${projectId}/workflows`, data),
  update: (id: string, data: any) => api.put(`/workflows/${id}`, data),
  delete: (id: string) => api.delete(`/workflows/${id}`),
  execute: (id: string, variables?: any) => api.post(`/workflows/${id}/execute`, { variables }),
  getRun: (id: string, runId: string) => api.get(`/workflows/${id}/runs/${runId}`),
  listRuns: (id: string) => api.get(`/workflows/${id}/runs`),
  cancelRun: (id: string, runId: string) => api.post(`/workflows/${id}/runs/${runId}/cancel`),
};

// Agents
export const agentsApi = {
  list: (projectId: string) => api.get(`/projects/${projectId}/agents`),
  get: (id: string) => api.get(`/agents/${id}`),
  create: (projectId: string, data: any) => api.post(`/projects/${projectId}/agents`, data),
  update: (id: string, data: any) => api.put(`/agents/${id}`, data),
  delete: (id: string) => api.delete(`/agents/${id}`),
  execute: (id: string, task: string, context?: any) => api.post(`/agents/${id}/execute`, { task, context }),
  getExecutions: (id: string) => api.get(`/agents/${id}/executions`),
};

// Knowledge Base
export const knowledgeBaseApi = {
  listBases: (projectId: string) => api.get(`/projects/${projectId}/knowledge-bases`),
  getBase: (id: string) => api.get(`/knowledge-bases/${id}`),
  createBase: (projectId: string, data: any) => api.post(`/projects/${projectId}/knowledge-bases`, data),
  updateBase: (id: string, data: any) => api.put(`/knowledge-bases/${id}`, data),
  deleteBase: (id: string) => api.delete(`/knowledge-bases/${id}`),
  
  listEntries: (baseId: string, params?: any) => api.get(`/knowledge-bases/${baseId}/entries`, { params }),
  getEntry: (id: string) => api.get(`/knowledge-entries/${id}`),
  createEntry: (baseId: string, data: any) => api.post(`/knowledge-bases/${baseId}/entries`, data),
  updateEntry: (id: string, data: any) => api.put(`/knowledge-entries/${id}`, data),
  deleteEntry: (id: string) => api.delete(`/knowledge-entries/${id}`),
  
  search: (baseId: string, query: string, params?: any) => api.post(`/knowledge-bases/${baseId}/search`, { query, ...params }),
  getContext: (baseId: string, query: string, params?: any) => api.post(`/knowledge-bases/${baseId}/context`, { query, ...params }),
  ingestRepo: (baseId: string, data: any) => api.post(`/knowledge-bases/${baseId}/ingest-repo`, data),
  ingestFiles: (baseId: string, formData: FormData) => api.post(`/knowledge-bases/${baseId}/ingest-files`, formData, { headers: { 'Content-Type': 'multipart/form-data' } }),
};

export const pluginsApi = {
  listRegistry: (params?: any) => api.get('/plugins/registry', { params }),
  getPlugin: (slug: string) => api.get(`/plugins/registry/${slug}`),
  listInstalled: (projectId: string) => api.get(`/projects/${projectId}/plugins`),
  install: (projectId: string, slug: string, config?: any) => api.post(`/projects/${projectId}/plugins`, { slug, config }),
  uninstall: (projectId: string, slug: string) => api.delete(`/projects/${projectId}/plugins/${slug}`),
  update: (projectId: string, slug: string, config: any) => api.put(`/projects/${projectId}/plugins/${slug}`, config),
  getConfig: (projectId: string, slug: string) => api.get(`/projects/${projectId}/plugins/${slug}/config`),
  execute: (projectId: string, slug: string, action: string, params?: any) => api.post(`/projects/${projectId}/plugins/${slug}/execute`, { action, params }),
};

export const featureFlagsApi = {
  list: () => api.get('/feature-flags'),
  get: (name: string) => api.get(`/feature-flags/${name}`),
  create: (data: any) => api.post('/feature-flags', data),
  update: (name: string, data: any) => api.put(`/feature-flags/${name}`, data),
  delete: (name: string) => api.delete(`/feature-flags/${name}`),
  evaluate: (name: string, context?: any) => api.post(`/feature-flags/${name}/evaluate`, { context }),
};

export const verificationApi = {
  run: (data: any) => api.post('/verify', data),
  getStatus: (id: string) => api.get(`/verify/${id}`),
  getLogs: (id: string) => api.get(`/verify/${id}/logs`),
};

export const costApi = {
  getSummary: (params?: any) => api.get('/cost/summary', { params }),
  getBreakdown: (params?: any) => api.get('/cost/breakdown', { params }),
  getUsage: (params?: any) => api.get('/cost/usage', { params }),
  getForecast: (params?: any) => api.get('/cost/forecast', { params }),
};