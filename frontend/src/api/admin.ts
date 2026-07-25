import apiClient from "./client";
import type { ApiResponse, PaginatedResponse } from "@/types/api";
import type { GeneralSettings } from "@/types/settings";

export interface AdminUserFilters {
  page?: number;
  limit?: number;
  search?: string;
  role?: string;
  isActive?: boolean;
  sortBy?: string;
  sortOrder?: "asc" | "desc";
}

export interface AdminOrganizationFilters {
  page?: number;
  limit?: number;
  search?: string;
  isActive?: boolean;
  sortBy?: string;
  sortOrder?: "asc" | "desc";
}

export interface AdminUser {
  id: string;
  email: string;
  fullName: string;
  username: string;
  role: string;
  isActive: boolean;
  isVerified: boolean;
  lastLogin?: string;
  createdAt: string;
  updatedAt: string;
}

export interface AdminOrganization {
  id: string;
  name: string;
  slug: string;
  ownerId: string;
  ownerName: string;
  memberCount: number;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export const adminApi = {
  getUsers: async (filters?: AdminUserFilters): Promise<PaginatedResponse<AdminUser>> => {
    const response = await apiClient.get<PaginatedResponse<AdminUser>>("/admin/users", {
      params: filters,
    });
    return response.data;
  },

  updateUser: async (id: string, data: Partial<AdminUser>): Promise<AdminUser> => {
    const response = await apiClient.patch<ApiResponse<AdminUser>>(`/admin/users/${id}`, data);
    return response.data.data;
  },

  deleteUser: async (id: string): Promise<void> => {
    await apiClient.delete(`/admin/users/${id}`);
  },

  getOrganizations: async (filters?: AdminOrganizationFilters): Promise<PaginatedResponse<AdminOrganization>> => {
    const response = await apiClient.get<PaginatedResponse<AdminOrganization>>("/admin/organizations", {
      params: filters,
    });
    return response.data;
  },

  updateOrganization: async (id: string, data: Partial<AdminOrganization>): Promise<AdminOrganization> => {
    const response = await apiClient.patch<ApiResponse<AdminOrganization>>(`/admin/organizations/${id}`, data);
    return response.data.data;
  },

  getSystemSettings: async (): Promise<GeneralSettings> => {
    const response = await apiClient.get<ApiResponse<GeneralSettings>>("/admin/settings");
    return response.data.data;
  },

  updateSystemSettings: async (data: Partial<GeneralSettings>): Promise<GeneralSettings> => {
    const response = await apiClient.put<ApiResponse<GeneralSettings>>("/admin/settings", data);
    return response.data.data;
  },
};
