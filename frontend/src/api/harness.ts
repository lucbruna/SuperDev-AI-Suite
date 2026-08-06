import apiClient from "./client";

// ---------------------------------------------------------------------------
// Harness API client — domínios, agentes e skills do harness de avaliação,
// montado em /api/v1/harness (backend/api/v1/harness.py).
// ---------------------------------------------------------------------------

const HARNESS_BASE = "/harness";

export interface HarnessStatus {
  status?: string;
  [key: string]: unknown;
}

export interface HarnessDomain {
  id?: string;
  name?: string;
  [key: string]: unknown;
}

export interface HarnessAgent {
  id?: string;
  name?: string;
  status?: string;
  [key: string]: unknown;
}

export interface HarnessSkill {
  id?: string;
  name?: string;
  description?: string;
  [key: string]: unknown;
}

export interface TaskResponse {
  task_id?: string;
  status?: string;
  result?: unknown;
  [key: string]: unknown;
}

export const harnessApi = {
  async status(): Promise<HarnessStatus> {
    const { data } = await apiClient.get(`${HARNESS_BASE}/status`);
    return data;
  },

  async domains(): Promise<HarnessDomain[]> {
    const { data } = await apiClient.get(`${HARNESS_BASE}/domains`);
    return data;
  },

  async agents(): Promise<HarnessAgent[]> {
    const { data } = await apiClient.get(`${HARNESS_BASE}/agents`);
    return data;
  },

  async skills(): Promise<HarnessSkill[]> {
    const { data } = await apiClient.get(`${HARNESS_BASE}/skills`);
    return data;
  },

  async skill(skillId: string): Promise<HarnessSkill> {
    const { data } = await apiClient.get(`${HARNESS_BASE}/skills/${skillId}`);
    return data;
  },

  async execute(input: Record<string, unknown>): Promise<TaskResponse> {
    const { data } = await apiClient.post(`${HARNESS_BASE}/execute`, input);
    return data;
  },
};
