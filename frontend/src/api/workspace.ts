import apiClient from "./client";

// ---------------------------------------------------------------------------
// Workspace API client — sessões de workspace,
// montado em /api/v1/workspace (backend/workspace/router.py).
// ---------------------------------------------------------------------------

const WORKSPACE_BASE = "/workspace";

export interface WorkspaceSession {
  id: string;
  name?: string;
  project_id?: string;
  template?: string;
  status?: string;
  created_at?: string;
  [key: string]: unknown;
}

export interface WorkspaceHealth {
  status?: string;
  [key: string]: unknown;
}

export const workspaceApi = {
  async list(): Promise<WorkspaceSession[]> {
    const { data } = await apiClient.get(`${WORKSPACE_BASE}/sessions`);
    return data;
  },

  // Forma esperada pela página /workspace: retorna envelope { sessions }.
  async listSessions(): Promise<{ sessions: WorkspaceSession[] }> {
    const { data } = await apiClient.get(`${WORKSPACE_BASE}/sessions`);
    if (data && typeof data === "object" && "sessions" in data) {
      return data as { sessions: WorkspaceSession[] };
    }
    return { sessions: Array.isArray(data) ? data : [] };
  },

  async create(input: { name: string; project_id?: string; description?: string }): Promise<WorkspaceSession> {
    const { data } = await apiClient.post(`${WORKSPACE_BASE}/sessions`, input);
    return data;
  },

  async createSession(input: {
    name: string;
    project_id?: string;
    description?: string;
  }): Promise<WorkspaceSession> {
    const { data } = await apiClient.post(`${WORKSPACE_BASE}/sessions`, input);
    return data;
  },

  async get(id: string): Promise<WorkspaceSession> {
    const { data } = await apiClient.get(`${WORKSPACE_BASE}/sessions/${id}`);
    return data;
  },

  async remove(id: string): Promise<Record<string, unknown>> {
    const { data } = await apiClient.delete(`${WORKSPACE_BASE}/sessions/${id}`);
    return data;
  },

  async deleteSession(id: string): Promise<Record<string, unknown>> {
    const { data } = await apiClient.delete(`${WORKSPACE_BASE}/sessions/${id}`);
    return data;
  },

  async health(): Promise<WorkspaceHealth> {
    const { data } = await apiClient.get(`${WORKSPACE_BASE}/health`);
    return data;
  },
};
