export interface MetricPoint {
  label: string;
  value: number;
  timestamp: string;
}

export interface ServiceHealth {
  name: string;
  status: "healthy" | "degraded" | "unhealthy";
  uptime: number;
  latency: number;
  lastChecked: string;
}

export interface Alert {
  id: string;
  name: string;
  severity: "info" | "warning" | "critical";
  status: "active" | "acknowledged" | "resolved";
  message: string;
  service: string;
  timestamp: string;
  acknowledgedAt?: string;
}

export interface LogEntry {
  id: string;
  timestamp: string;
  level: "info" | "warn" | "error" | "debug";
  source: string;
  message: string;
  context: Record<string, unknown>;
}
