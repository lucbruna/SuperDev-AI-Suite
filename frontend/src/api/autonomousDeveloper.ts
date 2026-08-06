import apiClient from "./client";

// ---------------------------------------------------------------------------
// Autonomous Developer API client — connects the dashboard to the module
// backend mounted at /api/v1/autonomous-developer (backend/app.py, volume 3
// module).
// ---------------------------------------------------------------------------

const AUTONOMOUS_DEVELOPER_BASE = "/autonomous-developer";

// The module router returns the backend envelope { success, data }.
function unwrap<T>(payload: unknown): T {
  if (payload && typeof payload === "object") {
    const obj = payload as { data?: T };
    if ("data" in obj) return obj.data as T;
  }
  return payload as T;
}

export interface DeveloperStatus {
  state?: Record<string, unknown>;
  stats?: Record<string, number | string>;
  registry?: Record<string, number>;
  memory?: Record<string, unknown>;
  sessions_active?: number;
  artifacts?: string[];
  config?: {
    name?: string;
    version?: string;
    mode?: string;
    work_branch?: string;
    project_root?: string;
  };
}

export interface DeveloperExecuteResult {
  state?: Record<string, unknown>;
  stats?: Record<string, unknown>;
  session_id?: string;
  artifacts?: string[];
}

export interface DeveloperSession {
  session_id?: string;
  created_at?: number;
  finished_at?: number | null;
  elapsed_seconds?: number;
  project_root?: string;
  status?: string;
  goal?: string;
  meta?: Record<string, unknown>;
}

export interface DeveloperSessions {
  active?: DeveloperSession[];
  recent?: DeveloperSession[];
}

export const autonomousDeveloperApi = {
  async status(): Promise<DeveloperStatus> {
    const { data } = await apiClient.get(`${AUTONOMOUS_DEVELOPER_BASE}/status`);
    return unwrap<DeveloperStatus>(data);
  },

  async execute(input: {
    goal: string;
    meta?: Record<string, unknown>;
    phases?: string[];
  }): Promise<DeveloperExecuteResult> {
    const { data } = await apiClient.post(
      `${AUTONOMOUS_DEVELOPER_BASE}/execute`,
      input,
    );
    return unwrap<DeveloperExecuteResult>(data);
  },

  async reset(): Promise<{ reset?: boolean }> {
    const { data } = await apiClient.post(`${AUTONOMOUS_DEVELOPER_BASE}/reset`);
    return unwrap<{ reset?: boolean }>(data);
  },

  async sessions(limit = 10): Promise<DeveloperSessions> {
    const { data } = await apiClient.get(`${AUTONOMOUS_DEVELOPER_BASE}/sessions`, {
      params: { limit },
    });
    return unwrap<DeveloperSessions>(data);
  },
};
