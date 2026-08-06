import apiClient from "./client";

// ---------------------------------------------------------------------------
// Data API client — export/import de dados, montado em /api/v1/data.
// ---------------------------------------------------------------------------

const DATA_BASE = "/data";

export interface ExportJob {
  id?: string;
  format?: string;
  status?: string;
  download_url?: string;
  created_at?: string;
  [key: string]: unknown;
}

export interface ImportJob {
  id?: string;
  status?: string;
  imported?: number;
  [key: string]: unknown;
}

export const dataApi = {
  async export(format = "json", collections?: string[]): Promise<ExportJob> {
    const { data } = await apiClient.post(`${DATA_BASE}/export`, { format, collections });
    return data;
  },

  async exports(): Promise<ExportJob[]> {
    const { data } = await apiClient.get(`${DATA_BASE}/exports`);
    return data;
  },

  async imports(): Promise<ImportJob[]> {
    const { data } = await apiClient.get(`${DATA_BASE}/imports`);
    return data;
  },

  async importJson(payload: Record<string, unknown>): Promise<ImportJob> {
    const { data } = await apiClient.post(`${DATA_BASE}/import/json`, payload);
    return data;
  },

  async importCsv(input: { collection: string; csv: string }): Promise<ImportJob> {
    const { data } = await apiClient.post(`${DATA_BASE}/import/csv`, input);
    return data;
  },
};
