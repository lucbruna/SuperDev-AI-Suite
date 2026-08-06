import apiClient from "./client";

// ---------------------------------------------------------------------------
// Builders API client — build/geração de apps, montado em /api/v1/builders.
// Rotas reais: GET "", POST /{builder_id}/build, POST /all/build.
// ---------------------------------------------------------------------------

const BUILDERS_BASE = "/builders";

export interface BuilderInfo {
  id?: string;
  name?: string;
  description?: string;
  enabled?: boolean;
  [key: string]: unknown;
}

export interface BuildResult {
  builder?: string;
  status?: string;
  output?: string;
  [key: string]: unknown;
}

export const buildersApi = {
  async list(): Promise<BuilderInfo[]> {
    const { data } = await apiClient.get(`${BUILDERS_BASE}`);
    return data;
  },

  async buildAll(payload: Record<string, unknown> = {}): Promise<BuildResult[]> {
    const { data } = await apiClient.post(`${BUILDERS_BASE}/all/build`, payload);
    return data;
  },

  async buildOne(builderId: string, payload: Record<string, unknown> = {}): Promise<BuildResult> {
    const { data } = await apiClient.post(`${BUILDERS_BASE}/${builderId}/build`, payload);
    return data;
  },
};
