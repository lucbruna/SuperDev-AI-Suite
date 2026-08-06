import apiClient from "./client";

// ---------------------------------------------------------------------------
// Cost API client — resumo, breakdown, uso e forecast de custos,
// montado em /api/v1/cost (backend/api/v1/cost.py).
// ---------------------------------------------------------------------------

const COST_BASE = "/cost";

export interface CostSummary {
  total?: number;
  period?: string;
  [key: string]: unknown;
}

export interface CostBreakdownItem {
  category?: string;
  cost?: number;
  [key: string]: unknown;
}

export interface CostUsage {
  [key: string]: unknown;
}

export interface CostForecast {
  [key: string]: unknown;
}

export const costApi = {
  async summary(): Promise<CostSummary> {
    const { data } = await apiClient.get(`${COST_BASE}/summary`);
    return data;
  },

  async breakdown(): Promise<CostBreakdownItem[]> {
    const { data } = await apiClient.get(`${COST_BASE}/breakdown`);
    return data;
  },

  async usage(): Promise<CostUsage> {
    const { data } = await apiClient.get(`${COST_BASE}/usage`);
    return data;
  },

  async forecast(): Promise<CostForecast> {
    const { data } = await apiClient.get(`${COST_BASE}/forecast`);
    return data;
  },
};
