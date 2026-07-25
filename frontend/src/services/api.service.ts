import { ENV } from "../config/environment";

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
    const token = localStorage.getItem("token");
    return {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };
  }
}
