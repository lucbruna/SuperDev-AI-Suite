import apiClient from "./client";
import type { ApiResponse } from "@/types/api";
import type { MetricPoint, ServiceHealth, Alert, LogEntry } from "@/types/monitoring";

export interface MetricsTimeRange {
  start: string;
  end: string;
  granularity?: string;
}

export interface AlertFilters {
  severity?: string;
  status?: string;
  service?: string;
  search?: string;
  page?: number;
  limit?: number;
}

export interface LogFilters {
  level?: string;
  source?: string;
  startDate?: string;
  endDate?: string;
  search?: string;
  page?: number;
  limit?: number;
}

export const monitoringApi = {
  getMetrics: async (timeRange: MetricsTimeRange): Promise<MetricPoint[]> => {
    const response = await apiClient.get<ApiResponse<MetricPoint[]>>("/monitoring/metrics", {
      params: timeRange,
    });
    return response.data.data;
  },

  getServiceHealth: async (): Promise<ServiceHealth[]> => {
    const response = await apiClient.get<ApiResponse<ServiceHealth[]>>("/monitoring/services");
    return response.data.data;
  },

  getAlerts: async (filters?: AlertFilters): Promise<Alert[]> => {
    const response = await apiClient.get<ApiResponse<Alert[]>>("/monitoring/alerts", {
      params: filters,
    });
    return response.data.data;
  },

  acknowledgeAlert: async (id: string): Promise<Alert> => {
    const response = await apiClient.post<ApiResponse<Alert>>(`/monitoring/alerts/${id}/acknowledge`);
    return response.data.data;
  },

  resolveAlert: async (id: string): Promise<Alert> => {
    const response = await apiClient.post<ApiResponse<Alert>>(`/monitoring/alerts/${id}/resolve`);
    return response.data.data;
  },

  getLogs: async (filters?: LogFilters): Promise<LogEntry[]> => {
    const response = await apiClient.get<ApiResponse<LogEntry[]>>("/monitoring/logs", {
      params: filters,
    });
    return response.data.data;
  },
};
