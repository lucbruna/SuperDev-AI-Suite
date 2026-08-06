import apiClient from "./client";

// ---------------------------------------------------------------------------
// AI Evolution Engine API client — connects the dashboard to the module
// backend mounted at /api/v1/evolution (backend/app.py, volume 5 module).
// ---------------------------------------------------------------------------

const EVOLUTION_BASE = "/evolution";

export interface EvolutionState {
  running?: boolean;
  cycles?: number;
  last_analysis_score?: number;
  open_recommendations?: number;
  open_decisions?: number;
  ticks?: number;
}

export interface EvolutionRecommendation {
  kind?: string;
  title?: string;
  description?: string;
  target?: string;
  severity?: string;
  impact_score?: number;
  effort_score?: number;
  risk_score?: number;
  status?: string;
  evidence?: string[];
  priority?: number;
}

export interface EvolutionAnalysis {
  score?: number;
  sections?: Record<string, unknown>;
  artifacts?: Record<string, unknown>;
}

export interface EvolutionIntegrationSummary {
  [name: string]: boolean | string | Record<string, unknown>;
}

export interface EvolutionDashboard {
  engine?: EvolutionState;
  integrations?: EvolutionIntegrationSummary;
}

export const evolutionApi = {
  async status(): Promise<{ state?: EvolutionState }> {
    const { data } = await apiClient.get(`${EVOLUTION_BASE}/status`);
    return data;
  },

  async analyze(): Promise<{ analysis?: EvolutionAnalysis }> {
    const { data } = await apiClient.post(`${EVOLUTION_BASE}/analyze`);
    return data;
  },

  async recommend(
    input: Partial<EvolutionRecommendation>,
  ): Promise<{ recommendation?: EvolutionRecommendation }> {
    const { data } = await apiClient.post(`${EVOLUTION_BASE}/recommend`, input);
    return data;
  },

  async approve(recommendation_id: string): Promise<Record<string, unknown>> {
    const { data } = await apiClient.post(`${EVOLUTION_BASE}/approve`, {
      recommendation_id,
    });
    return data;
  },

  async reject(recommendation_id: string): Promise<Record<string, unknown>> {
    const { data } = await apiClient.post(`${EVOLUTION_BASE}/reject`, {
      recommendation_id,
    });
    return data;
  },

  async start(): Promise<Record<string, unknown>> {
    const { data } = await apiClient.post(`${EVOLUTION_BASE}/start`);
    return data;
  },

  async stop(): Promise<Record<string, unknown>> {
    const { data } = await apiClient.post(`${EVOLUTION_BASE}/stop`);
    return data;
  },

  async integrations(): Promise<EvolutionIntegrationSummary> {
    const { data } = await apiClient.get(`${EVOLUTION_BASE}/integrations`);
    return data;
  },

  async dashboard(): Promise<EvolutionDashboard> {
    const { data } = await apiClient.get(`${EVOLUTION_BASE}/dashboard`);
    return data;
  },
};
