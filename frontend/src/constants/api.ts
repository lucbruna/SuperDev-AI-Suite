export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "/api/v1";

export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: "/auth/login",
    REGISTER: "/auth/register",
    LOGOUT: "/auth/logout",
    REFRESH: "/auth/refresh",
    ME: "/auth/me",
    VERIFY_EMAIL: "/auth/verify-email",
    FORGOT_PASSWORD: "/auth/forgot-password",
    RESET_PASSWORD: "/auth/reset-password",
  },
  USERS: {
    BASE: "/users",
    PROFILE: (id: string) => `/users/${id}`,
    PREFERENCES: "/users/preferences",
    UPDATE_PASSWORD: "/users/password",
  },
  PROJECTS: {
    BASE: "/projects",
    DETAIL: (id: string) => `/projects/${id}`,
    MEMBERS: (id: string) => `/projects/${id}/members`,
    STATS: (id: string) => `/projects/${id}/stats`,
  },
  HEALTH: {
    CHECK: "/health",
    READY: "/health/ready",
    LIVE: "/health/live",
  },
  WORKSPACE: {
    BASE: "/workspace",
    SESSIONS: "/workspace/sessions",
    SESSION: (id: string) => `/workspace/sessions/${id}`,
  },
  LLM: {
    PROVIDERS: "/llm/providers",
    PROVIDER_DETAIL: (name: string) => `/llm/providers/${name}`,
    PROVIDER_TEST: (name: string) => `/llm/providers/${name}/test`,
    MODELS: "/llm/models",
    CHAT: "/llm/chat",
    CHAT_STREAM: "/llm/chat/stream",
    HEALTH: "/llm/health",
  },
  DASHBOARD: {
    BASE: "/system/dashboard",
  },
  AGENTS: {
    BASE: "/agents",
  },
  WORKFLOWS: {
    BASE: "/workflows",
  },
  ARCHITECTURE_GRAPH: {
    BASE: "/architecture-graph",
    HEALTH: "/architecture-graph/health",
    STATS: "/architecture-graph/stats",
    ANALYZE: "/architecture-graph/analyze",
    INSIGHTS: "/architecture-graph/insights",
    RISK: "/architecture-graph/insights/risk",
    SEARCH: "/architecture-graph/search",
    EXPORT: (fmt: string) => `/architecture-graph/export/${fmt}`,
    REPORTS: (kind: string) => `/architecture-graph/reports/${kind}`,
  },
  ARCHITECTURE_INTELLIGENCE: {
    BASE: "/architecture-intelligence",
    METRICS: "/architecture-intelligence/metrics",
    INSIGHTS: "/architecture-intelligence/insights",
    PLAN: "/architecture-intelligence/plan",
    FORECAST: "/architecture-intelligence/forecast",
    TRENDS: "/architecture-intelligence/trends",
    OPTIMIZE: "/architecture-intelligence/optimize",
    DIAGNOSE: "/architecture-intelligence/diagnose",
    AGENTS: "/architecture-intelligence/agents",
    HISTORY: "/architecture-intelligence/history",
    SNAPSHOT: "/architecture-intelligence/snapshot",
    ASK: "/architecture-intelligence/ask",
    REPORT: "/architecture-intelligence/report",
  },
} as const;

export const API_TIMEOUT = 30000;
export const AGENT_TIMEOUT = 300000; // 5 minutes for agent tasks
export const API_RETRY_COUNT = 3;
export const API_RETRY_DELAY = 1000;
