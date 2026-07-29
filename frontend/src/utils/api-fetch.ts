/**
 * API fetch helper.
 *
 * Use instead of raw `fetch("/api/...")` to automatically:
 * - Prepend the configured API base URL
 * - Attach the JWT auth token
 * - Refresh expired tokens via the interceptor in apiClient
 *
 * Usage:
 *   import { api } from "@/utils/api-fetch";
 *   const data = await api.get("/workflows");
 *   const result = await api.post("/workflows/execute", { ... });
 */

import { ENV } from "@/config/environment";
import { useAuthStore } from "@/stores/authStore";

function authHeaders(): Record<string, string> {
  const token = useAuthStore.getState().accessToken;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const base = ENV.API_URL; // http://localhost:8000 (sem /api/v1 — rotas externas usam /api/...)
  const url = `${base}${path.startsWith("/") ? "" : "/"}${path}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
      ...(options.headers as Record<string, string>),
    },
  });
  if (!res.ok) {
    throw new Error(`API ${res.status}: ${res.statusText}`);
  }
  const json = await res.json();
  // Unwrap {success, data} envelope if present
  return (json.data ?? json) as T;
}

export const api = {
  get: <T>(path: string): Promise<T> => request<T>(path),
  post: <T>(path: string, body?: unknown): Promise<T> =>
    request<T>(path, { method: "POST", body: body ? JSON.stringify(body) : undefined }),
  put: <T>(path: string, body?: unknown): Promise<T> =>
    request<T>(path, { method: "PUT", body: body ? JSON.stringify(body) : undefined }),
  patch: <T>(path: string, body?: unknown): Promise<T> =>
    request<T>(path, { method: "PATCH", body: body ? JSON.stringify(body) : undefined }),
  delete: <T>(path: string): Promise<T> =>
    request<T>(path, { method: "DELETE" }),
};
