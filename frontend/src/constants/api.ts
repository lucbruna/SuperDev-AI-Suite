export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

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
} as const;

export const API_TIMEOUT = 30000;
export const API_RETRY_COUNT = 3;
export const API_RETRY_DELAY = 1000;
