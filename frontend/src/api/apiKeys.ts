import apiClient from "./client";

// ---------------------------------------------------------------------------
// API Keys client — listagem, criação e revogação de chaves,
// montado em /api/v1/api-keys (backend/api/v1/api_keys.py).
// ---------------------------------------------------------------------------

const API_KEYS_BASE = "/api-keys";

export interface ApiKey {
  id?: string;
  name?: string;
  prefix?: string;
  created_at?: string;
  last_used_at?: string;
  active?: boolean;
  [key: string]: unknown;
}

export const apiKeysApi = {
  async list(): Promise<ApiKey[]> {
    const { data } = await apiClient.get(`${API_KEYS_BASE}`);
    return data;
  },

  async create(input: { name: string; expires_at?: string }): Promise<ApiKey & { key?: string }> {
    const { data } = await apiClient.post(`${API_KEYS_BASE}`, input);
    return data;
  },

  async revoke(id: string): Promise<Record<string, unknown>> {
    const { data } = await apiClient.delete(`${API_KEYS_BASE}/${id}`);
    return data;
  },
};
