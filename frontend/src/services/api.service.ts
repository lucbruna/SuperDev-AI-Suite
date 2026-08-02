/**
 * @deprecated Use the axios-based `apiClient` from `@/api/client` instead.
 * It is the unified API client for the app: it attaches the JWT from the
 * auth store, auto-refreshes expired tokens, and retries failed requests.
 * This fetch-based service is kept only for backwards compatibility with
 * external consumers of this package and no longer reads a stale
 * `localStorage` key — it reads the live session from the auth store.
 */
import { ENV } from "../config/environment";
import { useAuthStore } from "../stores/authStore";

export class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string = ENV.API_URL) {
    this.baseUrl = baseUrl;
  }

  async get<T>(path: string): Promise<T> {
    const resp = await fetch(`${this.baseUrl}${path}`, {
      headers: this.getHeaders(),
    });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return resp.json();
  }

  async post<T>(path: string, body: unknown): Promise<T> {
    const resp = await fetch(`${this.baseUrl}${path}`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify(body),
    });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return resp.json();
  }

  async put<T>(path: string, body: unknown): Promise<T> {
    const resp = await fetch(`${this.baseUrl}${path}`, {
      method: "PUT",
      headers: this.getHeaders(),
      body: JSON.stringify(body),
    });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return resp.json();
  }

  async delete(path: string): Promise<void> {
    const resp = await fetch(`${this.baseUrl}${path}`, {
      method: "DELETE",
      headers: this.getHeaders(),
    });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  }

  private getHeaders(): Record<string, string> {
    const token = useAuthStore.getState().accessToken;
    return {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };
  }
}
