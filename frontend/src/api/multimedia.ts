import apiClient from "./client";

// ---------------------------------------------------------------------------
// Autonomous Multimedia AI Engine API client — connects the dashboard to the
// real module backend mounted at /api/v1/multimedia (see backend/app.py).
// ---------------------------------------------------------------------------

const MULTIMEDIA_BASE = "/multimedia";

export interface SubsystemCapability {
  name: string;
  version: string;
  status: string;
  operations: string[];
  metadata?: Record<string, unknown>;
}

export interface MultimediaHealthSubsystem {
  status: string;
  details?: Record<string, unknown>;
}

export interface MultimediaHealth {
  status: string;
  subsystems: Record<string, MultimediaHealthSubsystem>;
  engine_version?: string;
}

export interface RunOperationResult {
  [key: string]: unknown;
}

export const multimediaApi = {
  async health(): Promise<MultimediaHealth> {
    const { data } = await apiClient.get(`${MULTIMEDIA_BASE}/health`);
    return data;
  },

  async capabilities(): Promise<{ subsystems: SubsystemCapability[]; count: number }> {
    const { data } = await apiClient.get(`${MULTIMEDIA_BASE}/capabilities`);
    return data;
  },

  async subsystemInfo(subsystem: string): Promise<SubsystemCapability> {
    const { data } = await apiClient.get(`${MULTIMEDIA_BASE}/subsystems/${subsystem}`);
    return data;
  },

  async run(subsystem: string, operation: string, params: Record<string, unknown> = {}): Promise<RunOperationResult> {
    const { data } = await apiClient.post(
      `${MULTIMEDIA_BASE}/subsystems/${subsystem}/${operation}`,
      params,
    );
    return data;
  },
};
