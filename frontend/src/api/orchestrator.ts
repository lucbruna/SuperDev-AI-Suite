import apiClient from "./client";

// ---------------------------------------------------------------------------
// Super AI Orchestrator API client — controla as tarefas do orquestrador
// multi-agente montado em /api/v1/orchestrator (módulo volume 6).
// ---------------------------------------------------------------------------

const ORCHESTRATOR_BASE = "/orchestrator";

export interface OrchestratorStatus {
  running?: boolean;
  mode?: string;
  kernel?: Record<string, unknown>;
  [key: string]: unknown;
}

export interface OrchestratorTask {
  seq?: number;
  kind?: string;
  title?: string;
  status?: string;
  priority?: string;
  owner?: string;
  created_at?: number;
  require_approval?: boolean;
  [key: string]: unknown;
}

export interface OrchestratorTasks {
  tasks?: OrchestratorTask[];
  [key: string]: unknown;
}

export interface OrchestratorHealth {
  status?: string;
  [key: string]: unknown;
}

export interface OrchestratorAnalytics {
  [key: string]: unknown;
}

export interface OrchestratorAuditEntry {
  [key: string]: unknown;
}

export interface OrchestratorMemory {
  namespaces?: string[];
  [key: string]: unknown;
}

export interface OrchestratorIntegrations {
  [name: string]: unknown;
}

export const orchestratorApi = {
  async status(): Promise<OrchestratorStatus> {
    const { data } = await apiClient.get(`${ORCHESTRATOR_BASE}/status`);
    return data;
  },

  async config(): Promise<Record<string, unknown>> {
    const { data } = await apiClient.get(`${ORCHESTRATOR_BASE}/config`);
    return data;
  },

  async governance(): Promise<Record<string, unknown>> {
    const { data } = await apiClient.get(`${ORCHESTRATOR_BASE}/governance`);
    return data;
  },

  async submitTask(input: {
    kind: string;
    title: string;
    payload?: Record<string, unknown>;
    priority?: string;
    owner_hint?: string;
    require_approval?: boolean;
  }): Promise<OrchestratorTask> {
    const { data } = await apiClient.post(`${ORCHESTRATOR_BASE}/tasks`, input);
    return data;
  },

  async tasks(status?: string): Promise<OrchestratorTasks> {
    const { data } = await apiClient.get(`${ORCHESTRATOR_BASE}/tasks`, {
      params: status ? { status } : undefined,
    });
    return data;
  },

  async task(seq: number): Promise<OrchestratorTask> {
    const { data } = await apiClient.get(`${ORCHESTRATOR_BASE}/tasks/${seq}`);
    return data;
  },

  async approve(seq: number): Promise<OrchestratorTask> {
    const { data } = await apiClient.post(`${ORCHESTRATOR_BASE}/tasks/${seq}/approve`);
    return data;
  },

  async reject(seq: number, reason = "rejected"): Promise<OrchestratorTask> {
    const { data } = await apiClient.post(`${ORCHESTRATOR_BASE}/tasks/${seq}/reject`, {
      reason,
    });
    return data;
  },

  async cancel(seq: number): Promise<OrchestratorTask> {
    const { data } = await apiClient.post(`${ORCHESTRATOR_BASE}/tasks/${seq}/cancel`);
    return data;
  },

  async pause(seq: number): Promise<OrchestratorTask> {
    const { data } = await apiClient.post(`${ORCHESTRATOR_BASE}/tasks/${seq}/pause`);
    return data;
  },

  async resume(seq: number): Promise<OrchestratorTask> {
    const { data } = await apiClient.post(`${ORCHESTRATOR_BASE}/tasks/${seq}/resume`);
    return data;
  },

  async rollback(seq: number): Promise<OrchestratorTask> {
    const { data } = await apiClient.post(`${ORCHESTRATOR_BASE}/tasks/${seq}/rollback`);
    return data;
  },

  async tick(slices?: number): Promise<Record<string, unknown>> {
    const { data } = await apiClient.post(`${ORCHESTRATOR_BASE}/tick`, {
      slices: slices ?? 1,
    });
    return data;
  },

  async health(): Promise<OrchestratorHealth> {
    const { data } = await apiClient.get(`${ORCHESTRATOR_BASE}/health`);
    return data;
  },

  async metrics(): Promise<Record<string, unknown>> {
    const { data } = await apiClient.get(`${ORCHESTRATOR_BASE}/metrics`);
    return data;
  },

  async analytics(): Promise<OrchestratorAnalytics> {
    const { data } = await apiClient.get(`${ORCHESTRATOR_BASE}/analytics`);
    return data;
  },

  async audit(): Promise<OrchestratorAuditEntry[]> {
    const { data } = await apiClient.get(`${ORCHESTRATOR_BASE}/audit`);
    return data;
  },

  async events(event_type?: string): Promise<unknown[]> {
    const { data } = await apiClient.get(`${ORCHESTRATOR_BASE}/events`, {
      params: event_type ? { event_type } : undefined,
    });
    return data;
  },

  async memoryNamespaces(): Promise<OrchestratorMemory> {
    const { data } = await apiClient.get(`${ORCHESTRATOR_BASE}/memory`);
    return data;
  },

  async memoryKeys(namespace: string): Promise<Record<string, unknown>> {
    const { data } = await apiClient.get(`${ORCHESTRATOR_BASE}/memory/${namespace}`);
    return data;
  },

  async memoryRemember(namespace: string, key: string, value: unknown): Promise<Record<string, unknown>> {
    const { data } = await apiClient.post(`${ORCHESTRATOR_BASE}/memory`, {
      namespace,
      key,
      value,
    });
    return data;
  },

  async integrations(): Promise<OrchestratorIntegrations> {
    const { data } = await apiClient.get(`${ORCHESTRATOR_BASE}/integrations`);
    return data;
  },

  async invoke(name: string, action = "invoke", body: Record<string, unknown> = {}): Promise<unknown> {
    const { data } = await apiClient.post(
      `${ORCHESTRATOR_BASE}/integrations/${name}/invoke`,
      { action, ...body },
    );
    return data;
  },

  async dashboard(): Promise<Record<string, unknown>> {
    const { data } = await apiClient.get(`${ORCHESTRATOR_BASE}/dashboard`);
    return data;
  },
};
