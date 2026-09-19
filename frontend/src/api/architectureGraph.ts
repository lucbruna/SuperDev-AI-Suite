import apiClient from "./client";
import { API_BASE_URL, AGENT_TIMEOUT } from "@/constants/api";

// ---------------------------------------------------------------------------
// Architecture Graph API client — connects the dashboard to the real module
// backend mounted at /api/v1/architecture-graph (see backend/app.py).
// ---------------------------------------------------------------------------

const GRAPH_BASE = "/architecture-graph";

export interface GraphHealth {
  status: string;
  service?: string;
  version?: string;
}

export interface GraphStats {
  available: boolean;
  nodes: number;
  edges: number;
  kinds?: Record<string, number>;
  layers?: Record<string, number>;
  last_build?: string | null;
}

export interface InsightItem {
  severity?: string;
  category?: string;
  title?: string;
  detail?: string;
  recommendation?: string;
  nodes?: string[];
  data?: Record<string, unknown>;
}

export interface SearchResult {
  id?: string;
  doc_id?: string;
  name?: string;
  kind?: string;
  path?: string;
  score?: number;
  text?: string;
}

export const architectureGraphApi = {
  async health(): Promise<GraphHealth> {
    const { data } = await apiClient.get<GraphHealth>(`${GRAPH_BASE}/health`);
    return data;
  },

  async stats(): Promise<GraphStats> {
    const { data } = await apiClient.get<GraphStats>(`${GRAPH_BASE}/stats`);
    return data;
  },

  async analyze(): Promise<Record<string, unknown>> {
    const { data } = await apiClient.get(`${GRAPH_BASE}/analyze`, {
      timeout: AGENT_TIMEOUT, // triggers ensure_graph(): full build on first load
    });
    return data;
  },

  async insights(): Promise<{ available?: boolean; insights?: InsightItem[] }> {
    const { data } = await apiClient.get(`${GRAPH_BASE}/insights`, {
      timeout: AGENT_TIMEOUT, // triggers ensure_graph(): full build on first load
    });
    return data;
  },

  async risk(limit = 5): Promise<{ available?: boolean; ranking?: InsightItem[] }> {
    const { data } = await apiClient.get(`${GRAPH_BASE}/insights/risk`, {
      params: { limit },
      timeout: AGENT_TIMEOUT, // triggers ensure_graph(): full build on first load
    });
    return data;
  },

  async search(q: string): Promise<{ available?: boolean; results?: SearchResult[] }> {
    const { data } = await apiClient.get(`${GRAPH_BASE}/search`, {
      params: { q, limit: 10 },
      timeout: AGENT_TIMEOUT, // builds graph + RAG index on first use
    });
    return data;
  },

  async report(kind: string): Promise<Record<string, unknown>> {
    const { data } = await apiClient.get(`${GRAPH_BASE}/reports/${kind}`, {
      timeout: AGENT_TIMEOUT, // triggers ensure_graph(): full build on first load
    });
    return data;
  },

  exportUrl(fmt: string): string {
    return `${API_BASE_URL}${GRAPH_BASE}/export/${fmt}`;
  },
};
