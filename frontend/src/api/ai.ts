import apiClient from "./client";

// ---------------------------------------------------------------------------
// AI modules API client — health, módulos, stats e integrações específicas
// montado em /api/v1/ai (backend/ai_api/router.py).
// ---------------------------------------------------------------------------

const AI_BASE = "/ai";

export interface AiModuleInfo {
  name?: string;
  description?: string;
  status?: string;
  enabled?: boolean;
  [key: string]: unknown;
}

export interface AiModuleStat {
  [key: string]: unknown;
}

export const aiApi = {
  async health(): Promise<Record<string, unknown>> {
    const { data } = await apiClient.get(`${AI_BASE}/health`);
    return data;
  },

  async modules(): Promise<AiModuleInfo[]> {
    const { data } = await apiClient.get(`${AI_BASE}/modules`);
    return data;
  },

  async stats(): Promise<Record<string, unknown>> {
    const { data } = await apiClient.get(`${AI_BASE}/stats`);
    return data;
  },

  async cybersecurityStats(): Promise<AiModuleStat> {
    const { data } = await apiClient.get(`${AI_BASE}/cybersecurity/stats`);
    return data;
  },

  async threats(): Promise<Record<string, unknown>> {
    const { data } = await apiClient.get(`${AI_BASE}/cybersecurity/threats`);
    return data;
  },

  async dataPlatformStats(): Promise<AiModuleStat> {
    const { data } = await apiClient.get(`${AI_BASE}/data-platform/stats`);
    return data;
  },

  async erpStats(): Promise<AiModuleStat> {
    const { data } = await apiClient.get(`${AI_BASE}/erp/stats`);
    return data;
  },

  async knowledgeStats(): Promise<AiModuleStat> {
    const { data } = await apiClient.get(`${AI_BASE}/knowledge/stats`);
    return data;
  },
};
