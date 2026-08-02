import apiClient from "./client";
import { API_ENDPOINTS } from "@/constants/api";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface DashboardKPIs {
  organizations: number;
  projects: number;
  workflows: number;
  agents: number;
  active_agents: number;
  knowledge_bases: number;
  plugins_installed: number;
  executions_today: number;
  executions_total: number;
  success_rate: number;
  cost_today_usd: number;
  cost_month_usd: number;
}

export interface HealthCheck {
  status: string;
  message: string;
  latency_ms: number;
}

export interface DashboardHealth {
  status: "healthy" | "degraded" | "unhealthy" | "unknown";
  checks: Record<string, HealthCheck>;
}

export interface DashboardMetrics {
  uptime_seconds: number;
  total_requests: number;
  total_errors: number;
  error_rate_pct: number;
  requests_by_endpoint: Record<string, number>;
}

export interface ActivityItem {
  id: string;
  type: string;
  title: string;
  message: string;
  actor: string;
  timestamp: string;
}

export interface SystemInfo {
  version: string;
  name: string;
  api_prefix: string;
}

export interface DashboardData {
  kpis: DashboardKPIs;
  health: DashboardHealth;
  metrics: DashboardMetrics;
  recent_activity: ActivityItem[];
  system: SystemInfo;
}

export interface DashboardResponse {
  success: boolean;
  data: DashboardData;
}

// ---------------------------------------------------------------------------
// API
// ---------------------------------------------------------------------------

export const dashboardApi = {
  /** Fetch aggregated dashboard data */
  async getDashboard(): Promise<DashboardData> {
    const { data } = await apiClient.get<DashboardResponse>(
      API_ENDPOINTS.DASHBOARD.BASE,
    );
    return data.data;
  },
};
