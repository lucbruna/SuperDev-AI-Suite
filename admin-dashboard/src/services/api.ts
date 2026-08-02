import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import type {
  Agent,
  AgentExecuteResult,
  AppNotification,
  ApiEnvelope,
  AuthResponseData,
  CostForecast,
  CostSummary,
  CostUsage,
  DashboardData,
  ExecutionsStats,
  FeatureFlag,
  KnowledgeBase,
  Organization,
  OrganizationMember,
  Paginated,
  PluginInstalled,
  PluginRegistryEntry,
  Project,
  ProjectListResponse,
  SearchResponse,
  User,
  Workflow,
  WorkflowRun,
} from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const ACCESS_TOKEN_KEY = 'superdev_access_token';
const REFRESH_TOKEN_KEY = 'superdev_refresh_token';

export const tokenStore = {
  getAccess: () => localStorage.getItem(ACCESS_TOKEN_KEY),
  getRefresh: () => localStorage.getItem(REFRESH_TOKEN_KEY),
  setTokens: (accessToken: string, refreshToken: string) => {
    localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  },
  clear: () => {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  },
};

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: { 'Content-Type': 'application/json' },
      timeout: 30000,
    });

    this.client.interceptors.request.use((config) => {
      const token = tokenStore.getAccess();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          tokenStore.clear();
          if (!window.location.pathname.startsWith('/login')) {
            window.location.href = '/login';
          }
        }
        return Promise.reject(error);
      }
    );
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const res = await this.client.get<T>(url, config);
    return res.data;
  }

  async post<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    const res = await this.client.post<T>(url, data, config);
    return res.data;
  }

  async put<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    const res = await this.client.put<T>(url, data, config);
    return res.data;
  }

  async patch<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    const res = await this.client.patch<T>(url, data, config);
    return res.data;
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const res = await this.client.delete<T>(url, config);
    return res.data;
  }
}

export const api = new ApiService();

/** Resolve a promise; on failure return the fallback (never throws). */
export async function withFallback<T>(promise: Promise<T>, fallback: T): Promise<T> {
  try {
    return await promise;
  } catch (err) {
    // eslint-disable-next-line no-console
    console.warn('[api] falling back after error:', err);
    return fallback;
  }
}

// ── Auth ────────────────────────────────────────────────────────────────

export const authApi = {
  login: (email: string, password: string) =>
    api.post<ApiEnvelope<AuthResponseData>>('/auth/login', { email, password }),
  register: (data: { email: string; password: string; username: string; full_name?: string }) =>
    api.post<ApiEnvelope<AuthResponseData>>('/auth/register', data),
  logout: () => api.post<{ success: boolean }>('/auth/logout'),
  me: () => api.get<ApiEnvelope<{ user: User }>>('/auth/me'),
  refresh: (refreshToken: string) =>
    api.post<ApiEnvelope<AuthResponseData>>('/auth/refresh', { refresh_token: refreshToken }),
};

// ── Organizations ───────────────────────────────────────────────────────

export const organizationsApi = {
  list: (params?: { page?: number; limit?: number }) =>
    api.get<ApiEnvelope<Paginated<Organization>>>('/organizations', { params }),
  my: () => api.get<ApiEnvelope<Paginated<Organization>>>('/organizations/my'),
  get: (id: string) => api.get<ApiEnvelope<Organization>>(`/organizations/${id}`),
  create: (data: { name: string; slug: string; description?: string; plan?: string }) =>
    api.post<ApiEnvelope<Organization>>('/organizations', data),
  update: (id: string, data: Partial<Organization>) =>
    api.patch<ApiEnvelope<Organization>>(`/organizations/${id}`, data),
  delete: (id: string) => api.delete<void>(`/organizations/${id}`),
  members: (id: string) =>
    api.get<ApiEnvelope<Paginated<OrganizationMember>>>(`/organizations/${id}/members`),
};

// ── Projects ────────────────────────────────────────────────────────────

export const projectsApi = {
  list: (params?: { page?: number; page_size?: number; search?: string }) =>
    api.get<ProjectListResponse>('/projects', { params }),
  get: (id: string) => api.get<Project>(`/projects/${id}`),
  create: (data: { name: string; description?: string }) =>
    api.post<Project>('/projects', data),
  update: (id: string, data: { name?: string; description?: string }) =>
    api.put<Project>(`/projects/${id}`, data),
  delete: (id: string) => api.delete<void>(`/projects/${id}`),
};

// ── Workflows ───────────────────────────────────────────────────────────

export const workflowsApi = {
  list: () => api.get<Workflow[]>('/workflows'),
  create: (data: {
    name: string;
    description?: string;
    steps: Array<Record<string, unknown>>;
    variables?: Record<string, unknown>;
    tags?: string[];
  }) => api.post<Workflow>('/workflows', data),
  execute: (id: string, variables?: Record<string, unknown>) =>
    api.post<{ run_id: string; workflow_id: string; status: string; result: Record<string, unknown> }>(
      `/workflows/${id}/execute`,
      { variables }
    ),
  getRun: (id: string, runId: string) =>
    api.get<Record<string, unknown>>(`/workflows/${id}/runs/${runId}`),
  cancelRun: (id: string, runId: string) =>
    api.post<Record<string, unknown>>(`/workflows/${id}/runs/${runId}/cancel`),
};

// ── Agents ──────────────────────────────────────────────────────────────

export const agentsApi = {
  list: () => api.get<Agent[]>('/agents'),
  get: (id: string) => api.get<Agent>(`/agents/${id}`),
  create: (data: {
    name: string;
    description?: string;
    agent_type?: string;
    model?: string;
    provider?: string;
    max_steps?: number;
    temperature?: number;
  }) => api.post<Agent>('/agents', data),
  start: (id: string) => api.post<Agent>(`/agents/${id}/start`),
  stop: (id: string) => api.post<Agent>(`/agents/${id}/stop`),
  execute: (id: string, input: string, context?: Record<string, unknown>) =>
    api.post<AgentExecuteResult>(`/agents/${id}/execute`, { input, context }),
  delete: (id: string) => api.delete<void>(`/agents/${id}`),
};

// ── Knowledge Base ──────────────────────────────────────────────────────

export const knowledgeBaseApi = {
  list: () => api.get<KnowledgeBase[]>('/knowledge/knowledge-bases'),
  get: (id: string) => api.get<KnowledgeBase>(`/knowledge/knowledge-bases/${id}`),
  create: (data: { name: string; description?: string; type?: string; is_public?: boolean }) =>
    api.post<KnowledgeBase>('/knowledge/knowledge-bases', data),
  delete: (id: string) => api.delete<void>(`/knowledge/knowledge-bases/${id}`),
  search: (query: string, knowledgeBaseIds?: string[]) =>
    api.post<{ results: Array<Record<string, unknown>>; total: number }>(
      '/knowledge/knowledge-bases/search',
      { query, knowledge_base_ids: knowledgeBaseIds }
    ),
};

// ── Plugins ─────────────────────────────────────────────────────────────

export const pluginsApi = {
  listRegistry: (params?: { plugin_type?: string; search?: string }) =>
    api.get<PluginRegistryEntry[]>('/plugins/registry', { params }),
  popular: () => api.get<PluginRegistryEntry[]>('/plugins/registry/popular'),
  categories: () => api.get<{ categories: string[] }>('/plugins/registry/categories'),
  listInstalled: () => api.get<PluginInstalled[]>('/plugins/installed'),
  install: (slug: string, config?: Record<string, unknown>) =>
    api.post<PluginInstalled>('/plugins/install', { slug, config }),
  enable: (slug: string) => api.post<{ success: boolean }>(`/plugins/${slug}/enable`),
  disable: (slug: string) => api.post<{ success: boolean }>(`/plugins/${slug}/disable`),
  uninstall: (slug: string) => api.delete<void>(`/plugins/${slug}`),
  updateConfig: (slug: string, config: Record<string, unknown>) =>
    api.put<Record<string, unknown>>(`/plugins/${slug}/config`, config),
};

// ── Feature Flags ───────────────────────────────────────────────────────

export const featureFlagsApi = {
  list: () => api.get<{ success: boolean; flags: FeatureFlag[] }>('/feature-flags'),
  get: (name: string) => api.get<{ success: boolean; flag: FeatureFlag }>(`/feature-flags/${name}`),
  toggle: (name: string) =>
    api.post<{ success: boolean; flag: string; enabled: boolean }>(`/feature-flags/${name}/toggle`),
  set: (name: string, enabled: boolean) =>
    api.put<{ success: boolean; flag: string; enabled: boolean }>(`/feature-flags/${name}`, { enabled }),
  delete: (name: string) => api.delete<{ success: boolean }>(`/feature-flags/${name}`),
  check: (name: string) =>
    api.get<{ success: boolean; name: string; enabled: boolean }>(`/feature-flags/check/${name}`),
};

// ── Executions ──────────────────────────────────────────────────────────

export const executionsApi = {
  statsToday: () =>
    api.get<ApiEnvelope<ExecutionsStats>>('/executions/stats/today'),
  list: (params?: { limit?: number; offset?: number }) =>
    api.get<ApiEnvelope<Paginated<WorkflowRun>> & { data: { items: WorkflowRun[]; total: number } }>(
      '/executions',
      { params }
    ),
};

// ── Cost ────────────────────────────────────────────────────────────────

export const costApi = {
  summary: () => api.get<ApiEnvelope<CostSummary>>('/cost/summary'),
  breakdown: () =>
    api.get<
      ApiEnvelope<{
        by_agent: Array<{ agent_id: string; count: number; total: number }>;
        tokens_by_agent: Array<{ agent_id: string; count: number; total: number }>;
      }>
    >('/cost/breakdown'),
  usage: () => api.get<ApiEnvelope<CostUsage>>('/cost/usage'),
  forecast: () => api.get<ApiEnvelope<CostForecast>>('/cost/forecast'),
};

// ── System / Dashboard ──────────────────────────────────────────────────

export const systemApi = {
  dashboard: () => api.get<ApiEnvelope<DashboardData>>('/system/dashboard'),
};

export const healthApi = {
  check: () => api.get<Record<string, unknown>>('/health'),
  version: () => api.get<Record<string, unknown>>('/version'),
};

// ── Notifications ───────────────────────────────────────────────────────

export const notificationsApi = {
  list: (unreadOnly = false) =>
    api.get<AppNotification[]>('/notifications', { params: { unread_only: unreadOnly } }),
  unreadCount: () => api.get<{ count: number }>('/notifications/unread-count'),
  markRead: (id: string) => api.post<{ success: boolean }>(`/notifications/${id}/read`),
  markAllRead: () => api.post<{ success: boolean }>('/notifications/read-all'),
  delete: (id: string) => api.delete<void>(`/notifications/${id}`),
};

// ── Search ──────────────────────────────────────────────────────────────

export const searchApi = {
  search: (query: string, type?: string, limit = 10) =>
    api.post<SearchResponse>('/search/search', { query, type, limit }),
  stats: () => api.get<Record<string, unknown>>('/search/stats'),
};

// ── Registry central ────────────────────────────────────────────────────

export const apiRegistry = {
  auth: authApi,
  organizations: organizationsApi,
  projects: projectsApi,
  workflows: workflowsApi,
  agents: agentsApi,
  knowledgeBase: knowledgeBaseApi,
  plugins: pluginsApi,
  featureFlags: featureFlagsApi,
  executions: executionsApi,
  cost: costApi,
  system: systemApi,
  health: healthApi,
  notifications: notificationsApi,
  search: searchApi,
};

export default apiRegistry;
