import apiClient from "./client";

// ---------------------------------------------------------------------------
// Search API client — indexação e busca no repositório,
// montado em /api/v1/search (backend/search/router.py).
// ---------------------------------------------------------------------------

const SEARCH_BASE = "/search";

export interface SearchResult {
  document?: unknown;
  score?: number;
  [key: string]: unknown;
}

export interface SearchStats {
  documents?: number;
  indexed_at?: string;
  [key: string]: unknown;
}

export const searchApi = {
  async index(input: Record<string, unknown>): Promise<Record<string, unknown>> {
    const { data } = await apiClient.post(`${SEARCH_BASE}/index`, input);
    return data;
  },

  async search(query: string, limit = 10): Promise<SearchResult[]> {
    const { data } = await apiClient.post(`${SEARCH_BASE}/search`, { query, limit });
    return data;
  },

  async deleteDocument(docId: string): Promise<Record<string, unknown>> {
    const { data } = await apiClient.delete(`${SEARCH_BASE}/documents/${docId}`);
    return data;
  },

  async documents(): Promise<SearchResult[]> {
    const { data } = await apiClient.get(`${SEARCH_BASE}/documents`);
    return data;
  },

  async stats(): Promise<SearchStats> {
    const { data } = await apiClient.get(`${SEARCH_BASE}/stats`);
    return data;
  },
};
