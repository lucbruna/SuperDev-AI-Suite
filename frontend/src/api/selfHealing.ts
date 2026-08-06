import apiClient from "./client";

// ---------------------------------------------------------------------------
// Self-Healing Engine API client — connects the dashboard to the module
// backend mounted at /api/v1/self-healing (backend/app.py, volume 3 module).
// ---------------------------------------------------------------------------

const SELF_HEALING_BASE = "/self-healing";

// The module router returns the backend envelope { success, data }.
function unwrap<T>(payload: unknown): T {
  if (payload && typeof payload === "object") {
    const obj = payload as { data?: T };
    if ("data" in obj) return obj.data as T;
  }
  return payload as T;
}

export interface HealingStatus {
  cycles?: number;
  events?: number;
  memory?: number;
  artifacts?: string[];
  summary?: {
    stats?: Record<string, unknown>;
    state?: Record<string, unknown>;
    events?: number;
    memory?: number;
    artifacts?: string[];
  };
}

export interface HealingRunResult {
  cycle?: number;
  pipeline?: {
    status?: string;
    phases?: string[];
    steps?: Array<Record<string, unknown>>;
  };
  event_sequence?: number;
}

export interface HealingEvent {
  event_type?: string;
  payload?: Record<string, unknown>;
  sequence?: number;
  timestamp?: number;
}

export interface HealingEvents {
  events?: HealingEvent[];
  last_sequence?: number;
}

export const selfHealingApi = {
  async status(): Promise<HealingStatus> {
    const { data } = await apiClient.get(`${SELF_HEALING_BASE}/status`);
    return unwrap<HealingStatus>(data);
  },

  async run(incident?: Record<string, unknown>): Promise<HealingRunResult> {
    const { data } = await apiClient.post(`${SELF_HEALING_BASE}/run`, {
      incident: incident ?? {},
    });
    return unwrap<HealingRunResult>(data);
  },

  async events(): Promise<HealingEvents> {
    const { data } = await apiClient.get(`${SELF_HEALING_BASE}/events`);
    return unwrap<HealingEvents>(data);
  },
};
