import apiClient from "./client";

// ---------------------------------------------------------------------------
// System API client — status, saúde, self-test, boot/shutdown, scheduler e
// métricas do backend montado em /api/v1/system.
// ---------------------------------------------------------------------------

const SYSTEM_BASE = "/system";

export interface SystemStatus {
  status?: string;
  started_at?: string;
  uptime_seconds?: number;
  version?: string;
  [key: string]: unknown;
}

export interface SystemHealth {
  status?: string;
  checks?: Record<string, unknown>;
  [key: string]: unknown;
}

export interface SelfTestResult {
  [key: string]: unknown;
}

export interface SchedulerTask {
  id?: string;
  name?: string;
  cron?: string;
  enabled?: boolean;
  [key: string]: unknown;
}

export interface SystemAgent {
  id?: string;
  name?: string;
  status?: string;
  [key: string]: unknown;
}

export const systemApi = {
  async status(): Promise<SystemStatus> {
    const { data } = await apiClient.get(`${SYSTEM_BASE}/status`);
    return data;
  },

  async health(): Promise<SystemHealth> {
    const { data } = await apiClient.get(`${SYSTEM_BASE}/health`);
    return data;
  },

  async selfTest(): Promise<SelfTestResult> {
    const { data } = await apiClient.get(`${SYSTEM_BASE}/self-test`);
    return data;
  },

  async boot(): Promise<Record<string, unknown>> {
    const { data } = await apiClient.post(`${SYSTEM_BASE}/boot`);
    return data;
  },

  async shutdown(): Promise<Record<string, unknown>> {
    const { data } = await apiClient.post(`${SYSTEM_BASE}/shutdown`);
    return data;
  },

  async agents(): Promise<SystemAgent[]> {
    const { data } = await apiClient.get(`${SYSTEM_BASE}/agents`);
    return data;
  },

  async startAgent(agentId: string): Promise<Record<string, unknown>> {
    const { data } = await apiClient.post(`${SYSTEM_BASE}/agents/${agentId}/start`);
    return data;
  },

  async stopAgent(agentId: string): Promise<Record<string, unknown>> {
    const { data } = await apiClient.post(`${SYSTEM_BASE}/agents/${agentId}/stop`);
    return data;
  },

  async executeAgent(input: Record<string, unknown>): Promise<Record<string, unknown>> {
    const { data } = await apiClient.post(`${SYSTEM_BASE}/agents/execute`, input);
    return data;
  },

  async schedulerTasks(): Promise<SchedulerTask[]> {
    const { data } = await apiClient.get(`${SYSTEM_BASE}/scheduler/tasks`);
    return data;
  },

  async runSchedulerTask(taskId: string): Promise<Record<string, unknown>> {
    const { data } = await apiClient.post(`${SYSTEM_BASE}/scheduler/run/${taskId}`);
    return data;
  },

  async metrics(): Promise<Record<string, unknown>> {
    const { data } = await apiClient.get(`${SYSTEM_BASE}/metrics`);
    return data;
  },
};
