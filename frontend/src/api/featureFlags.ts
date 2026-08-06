import apiClient from "./client";

// ---------------------------------------------------------------------------
// Feature Flags API client — lista, toggle e checagem de flags,
// montado em /api/v1/feature-flags (backend/api/v1/feature_flags.py).
// ---------------------------------------------------------------------------

const FLAGS_BASE = "/feature-flags";

export interface FeatureFlag {
  name?: string;
  enabled?: boolean;
  description?: string;
  [key: string]: unknown;
}

export interface FlagListEnvelope {
  success?: boolean;
  flags?: FeatureFlag[];
  [key: string]: unknown;
}

export interface FlagCheckEnvelope {
  success?: boolean;
  flag?: FeatureFlag;
  enabled?: boolean;
  [key: string]: unknown;
}

export const featureFlagsApi = {
  async list(): Promise<FlagListEnvelope> {
    const { data } = await apiClient.get(`${FLAGS_BASE}`);
    // O backend retorna { success, flags: { name: flag, ... } } — normaliza
    // para { success, flags: [{ name, ...flag }, ...] } para a UI listar.
    if (data && typeof data === "object" && !Array.isArray(data.flags) && data.flags) {
      const flags = Object.entries(data.flags as Record<string, unknown>).map(([name, flag]) => ({
        name,
        ...(flag && typeof flag === "object" ? (flag as Record<string, unknown>) : {}),
      }));
      return { ...data, flags };
    }
    return data;
  },

  async get(name: string): Promise<FlagCheckEnvelope> {
    const { data } = await apiClient.get(`${FLAGS_BASE}/${name}`);
    return data;
  },

  async toggle(name: string): Promise<FlagCheckEnvelope> {
    const { data } = await apiClient.post(`${FLAGS_BASE}/${name}/toggle`);
    return data;
  },

  async update(name: string, updates: Record<string, unknown>): Promise<FlagCheckEnvelope> {
    const { data } = await apiClient.put(`${FLAGS_BASE}/${name}`, updates);
    return data;
  },

  async remove(name: string): Promise<Record<string, unknown>> {
    const { data } = await apiClient.delete(`${FLAGS_BASE}/${name}`);
    return data;
  },

  async check(name: string): Promise<FlagCheckEnvelope> {
    const { data } = await apiClient.get(`${FLAGS_BASE}/check/${name}`);
    return data;
  },
};
