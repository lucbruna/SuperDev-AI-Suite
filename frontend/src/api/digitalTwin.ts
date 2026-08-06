import apiClient from "./client";

// ---------------------------------------------------------------------------
// Digital Twin API client — connects the dashboard to the module backend
// mounted at /api/v1/digital-twin (backend/app.py, volume 3 module).
// ---------------------------------------------------------------------------

const DIGITAL_TWIN_BASE = "/digital-twin";

// The module router returns the backend envelope { success, data }.
function unwrap<T>(payload: unknown): T {
  if (payload && typeof payload === "object") {
    const obj = payload as { data?: T };
    if ("data" in obj) return obj.data as T;
  }
  return payload as T;
}

export interface DigitalTwinState {
  running?: boolean;
  cycles?: number;
  twin_status?: string;
}

export interface DigitalTwinConfig {
  enabled?: boolean;
  name?: string;
  sync_interval_seconds?: number;
}

export interface DigitalTwinCycleResult {
  cycle?: number;
  pipeline?: Record<string, unknown>;
  event_sequence?: number;
}

export interface DigitalTwinBuildInput {
  name: string;
  raw_entities?: Array<{
    id: string;
    type: string;
    name: string;
  }>;
  relationships?: Array<[string, string, string]>;
}

export interface DigitalTwinSnapshot {
  twin_name?: string;
  sequence?: number;
  entities?: unknown[];
}

export interface DigitalTwinAnalysis {
  entity_count?: number;
  [key: string]: unknown;
}

export interface DigitalTwinValidation {
  valid?: boolean;
  [key: string]: unknown;
}

export const digitalTwinApi = {
  async status(): Promise<DigitalTwinState> {
    const { data } = await apiClient.get(`${DIGITAL_TWIN_BASE}/status`);
    return unwrap<DigitalTwinState>(data);
  },

  async endpoints(): Promise<{ endpoints?: string[] }> {
    const { data } = await apiClient.get(`${DIGITAL_TWIN_BASE}/endpoints`);
    return unwrap<{ endpoints?: string[] }>(data);
  },

  async config(): Promise<DigitalTwinConfig> {
    const { data } = await apiClient.get(`${DIGITAL_TWIN_BASE}/config`);
    return unwrap<DigitalTwinConfig>(data);
  },

  async start(): Promise<DigitalTwinState> {
    const { data } = await apiClient.post(`${DIGITAL_TWIN_BASE}/start`);
    return unwrap<DigitalTwinState>(data);
  },

  async stop(): Promise<DigitalTwinState> {
    const { data } = await apiClient.post(`${DIGITAL_TWIN_BASE}/stop`);
    return unwrap<DigitalTwinState>(data);
  },

  async cycle(): Promise<DigitalTwinCycleResult> {
    const { data } = await apiClient.post(`${DIGITAL_TWIN_BASE}/cycle`);
    return unwrap<DigitalTwinCycleResult>(data);
  },

  async tick(steps: number): Promise<{ steps?: number; cycles_ran?: number }> {
    const { data } = await apiClient.post(`${DIGITAL_TWIN_BASE}/tick`, { steps });
    return unwrap<{ steps?: number; cycles_ran?: number }>(data);
  },

  async buildTwin(input: DigitalTwinBuildInput): Promise<Record<string, unknown>> {
    const { data } = await apiClient.post(`${DIGITAL_TWIN_BASE}/build-twin`, input);
    return unwrap<Record<string, unknown>>(data);
  },

  async snapshot(name: string): Promise<DigitalTwinSnapshot> {
    const { data } = await apiClient.get(`${DIGITAL_TWIN_BASE}/snapshot`, {
      params: { name },
    });
    return unwrap<DigitalTwinSnapshot>(data);
  },

  async analyze(input: { name: string }): Promise<DigitalTwinAnalysis> {
    const { data } = await apiClient.post(`${DIGITAL_TWIN_BASE}/analyze`, input);
    return unwrap<DigitalTwinAnalysis>(data);
  },

  async validate(input: { name: string }): Promise<DigitalTwinValidation> {
    const { data } = await apiClient.post(`${DIGITAL_TWIN_BASE}/validate`, input);
    return unwrap<DigitalTwinValidation>(data);
  },
};
