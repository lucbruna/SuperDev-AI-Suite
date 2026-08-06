import apiClient from "./client";

// ---------------------------------------------------------------------------
// Executions API client — histórico e stats de execuções,
// montado em /api/v1/executions (backend/api/v1/executions.py).
// ---------------------------------------------------------------------------

const EXECUTIONS_BASE = "/executions";

export interface ExecutionEntry {
  id?: string;
  action?: string;
  status?: string;
  duration_ms?: number;
  created_at?: string;
  [key: string]: unknown;
}

export interface ExecutionStats {
  today?: number;
  total?: number;
  success_rate?: number;
  [key: string]: unknown;
}

export const executionsApi = {
  async list(params?: Record<string, unknown>): Promise<ExecutionEntry[]> {
    const { data } = await apiClient.get(`${EXECUTIONS_BASE}`, { params });
    return data;
  },

  async statsToday(): Promise<ExecutionStats> {
    const { data } = await apiClient.get(`${EXECUTIONS_BASE}/stats/today`);
    return data;
  },
};
