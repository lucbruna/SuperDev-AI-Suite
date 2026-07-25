import apiClient from "./client";
import type { ApiResponse } from "@/types/api";
import type { GeneralSettings, AppearanceSettings, ProviderConfig } from "@/types/settings";

export const settingsApi = {
  getGeneralSettings: async (): Promise<GeneralSettings> => {
    const response = await apiClient.get<ApiResponse<GeneralSettings>>("/settings/general");
    return response.data.data;
  },

  updateGeneralSettings: async (data: Partial<GeneralSettings>): Promise<GeneralSettings> => {
    const response = await apiClient.put<ApiResponse<GeneralSettings>>("/settings/general", data);
    return response.data.data;
  },

  getAppearanceSettings: async (): Promise<AppearanceSettings> => {
    const response = await apiClient.get<ApiResponse<AppearanceSettings>>("/settings/appearance");
    return response.data.data;
  },

  updateAppearanceSettings: async (data: Partial<AppearanceSettings>): Promise<AppearanceSettings> => {
    const response = await apiClient.put<ApiResponse<AppearanceSettings>>("/settings/appearance", data);
    return response.data.data;
  },

  getProviderConfigs: async (): Promise<ProviderConfig[]> => {
    const response = await apiClient.get<ApiResponse<ProviderConfig[]>>("/settings/providers");
    return response.data.data;
  },

  updateProviderConfig: async (id: string, data: Partial<ProviderConfig>): Promise<ProviderConfig> => {
    const response = await apiClient.put<ApiResponse<ProviderConfig>>(`/settings/providers/${id}`, data);
    return response.data.data;
  },

  testProviderConnection: async (id: string): Promise<{ success: boolean; message: string }> => {
    const response = await apiClient.post<ApiResponse<{ success: boolean; message: string }>>(
      `/settings/providers/${id}/test`,
    );
    return response.data.data;
  },
};
