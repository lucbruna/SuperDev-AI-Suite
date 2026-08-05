import apiClient from "./client";

// ---------------------------------------------------------------------------
// Architecture Intelligence API client — connects the dashboard to the real
// module backend mounted at /api/v1/architecture-intelligence (backend/app.py).
// ---------------------------------------------------------------------------

const INTEL_BASE = "/architecture-intelligence";

export interface TrendItem {
  metric?: string;
  label?: string;
  first?: number;
  last?: number;
  delta?: number;
  percent?: number;
  direction?: string;
}

export interface ForecastItem {
  metric?: string;
  last?: number;
  projected?: number[];
  slope_per_step?: number;
  direction?: string;
}

export interface InsightItem {
  id?: string;
  severity?: string;
  category?: string;
  title?: string;
  detail?: string;
  recommendation?: string;
  data?: Record<string, unknown>;
}

export interface PlanTask {
  id?: string;
  action?: string;
  detail?: string;
  severity?: string;
  effort?: string;
  category?: string;
}

export interface Recommendation {
  id?: string;
  priority?: string;
  category?: string;
  action?: string;
  detail?: string;
  impact?: string;
}

export interface CheckItem {
  name?: string;
  ok?: boolean;
  detail?: unknown;
}

export interface SnapshotItem {
  ts?: number;
  nodes?: number;
  edges?: number;
  score?: number;
  integrity_issues?: number;
}

export const architectureIntelligenceApi = {
  async metrics(): Promise<Record<string, unknown>> {
    const { data } = await apiClient.get(`${INTEL_BASE}/metrics`);
    return data;
  },

  async insights(): Promise<{ available?: boolean; insights?: InsightItem[] }> {
    const { data } = await apiClient.get(`${INTEL_BASE}/insights`);
    return data;
  },

  async plan(): Promise<{
    available?: boolean;
    summary?: string;
    effort?: Record<string, number>;
    tasks?: PlanTask[];
    total_tasks?: number;
    sequence?: string[];
  }> {
    const { data } = await apiClient.get(`${INTEL_BASE}/plan`);
    return data;
  },

  async forecast(): Promise<{
    available?: boolean;
    count?: number;
    forecasts?: ForecastItem[];
    message?: string;
  }> {
    const { data } = await apiClient.get(`${INTEL_BASE}/forecast`);
    return data;
  },

  async trends(): Promise<{
    available?: boolean;
    count?: number;
    trends?: TrendItem[];
    message?: string;
  }> {
    const { data } = await apiClient.get(`${INTEL_BASE}/trends`);
    return data;
  },

  async optimize(): Promise<{
    total?: number;
    recommendations?: Recommendation[];
  }> {
    const { data } = await apiClient.get(`${INTEL_BASE}/optimize`);
    return data;
  },

  async diagnose(): Promise<{
    status?: string;
    checks?: CheckItem[];
    checked_at?: string;
  }> {
    const { data } = await apiClient.get(`${INTEL_BASE}/diagnose`);
    return data;
  },

  async agents(): Promise<{
    agents?: Record<string, unknown>;
    count?: number;
    errors?: string[];
  }> {
    const { data } = await apiClient.get(`${INTEL_BASE}/agents`);
    return data;
  },

  async history(limit = 10): Promise<{
    available?: boolean;
    count?: number;
    snapshots?: SnapshotItem[];
  }> {
    const { data } = await apiClient.get(`${INTEL_BASE}/history`, {
      params: { limit },
    });
    return data;
  },

  async snapshot(): Promise<{
    available?: boolean;
    appended?: boolean;
    snapshot?: SnapshotItem;
  }> {
    const { data } = await apiClient.post(`${INTEL_BASE}/snapshot`);
    return data;
  },

  async ask(question: string): Promise<{
    available?: boolean;
    answer?: string;
    generator?: string;
  }> {
    const { data } = await apiClient.post(`${INTEL_BASE}/ask`, { question });
    return data;
  },

  async report(): Promise<Record<string, unknown>> {
    const { data } = await apiClient.get(`${INTEL_BASE}/report`);
    return data;
  },
};
