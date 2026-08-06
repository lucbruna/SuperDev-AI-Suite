import apiClient from "./client";

// ---------------------------------------------------------------------------
// Plugins API client — registry, instalação e ativação/desativação,
// montado em /api/v1/plugins (backend/api/v1/plugins.py).
// ---------------------------------------------------------------------------

const PLUGINS_BASE = "/plugins";

export interface PluginRegistryEntry {
  slug?: string;
  name?: string;
  description?: string;
  category?: string;
  installed?: boolean;
  enabled?: boolean;
  version?: string;
  [key: string]: unknown;
}

export interface PluginInstalled {
  slug?: string;
  enabled?: boolean;
  [key: string]: unknown;
}

export const pluginsApi = {
  async registry(): Promise<PluginRegistryEntry[]> {
    const { data } = await apiClient.get(`${PLUGINS_BASE}/registry`);
    return data;
  },

  async popular(): Promise<PluginRegistryEntry[]> {
    const { data } = await apiClient.get(`${PLUGINS_BASE}/registry/popular`);
    return data;
  },

  async categories(): Promise<string[]> {
    const { data } = await apiClient.get(`${PLUGINS_BASE}/registry/categories`);
    return data;
  },

  async installed(): Promise<PluginInstalled[]> {
    const { data } = await apiClient.get(`${PLUGINS_BASE}/installed`);
    return data;
  },

  async install(slug: string): Promise<PluginInstalled> {
    const { data } = await apiClient.post(`${PLUGINS_BASE}/install`, { slug });
    return data;
  },

  async enable(slug: string): Promise<PluginInstalled> {
    const { data } = await apiClient.post(`${PLUGINS_BASE}/${slug}/enable`);
    return data;
  },

  async disable(slug: string): Promise<PluginInstalled> {
    const { data } = await apiClient.post(`${PLUGINS_BASE}/${slug}/disable`);
    return data;
  },

  async uninstall(slug: string): Promise<Record<string, unknown>> {
    const { data } = await apiClient.delete(`${PLUGINS_BASE}/${slug}`);
    return data;
  },

  async updateConfig(slug: string, config: Record<string, unknown>): Promise<PluginInstalled> {
    const { data } = await apiClient.put(`${PLUGINS_BASE}/${slug}/config`, { config });
    return data;
  },
};
