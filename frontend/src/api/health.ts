import apiClient from "./client";
import { API_ENDPOINTS } from "@/constants/api";
import type { ApiResponse } from "@/types/api";

interface HealthStatus {
  status: string;
  version: string;
  uptime: number;
  timestamp: string;
}

export const healthApi = {
  check: async (): Promise<HealthStatus> => {
    const response = await apiClient.get<ApiResponse<HealthStatus>>(
      API_ENDPOINTS.HEALTH.CHECK,
    );
    return response.data.data;
  },

  ready: async (): Promise<HealthStatus> => {
    const response = await apiClient.get<ApiResponse<HealthStatus>>(
      API_ENDPOINTS.HEALTH.READY,
    );
    return response.data.data;
  },

  live: async (): Promise<HealthStatus> => {
    const response = await apiClient.get<ApiResponse<HealthStatus>>(
      API_ENDPOINTS.HEALTH.LIVE,
    );
    return response.data.data;
  },
};
