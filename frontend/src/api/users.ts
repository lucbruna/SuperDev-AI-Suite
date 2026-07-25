import apiClient from "./client";
import { API_ENDPOINTS } from "@/constants/api";
import type { UserProfile, UpdateUserRequest, UpdatePasswordRequest } from "@/types/user";
import type { ApiResponse, PaginatedResponse } from "@/types/api";
import type { UserListParams } from "@/types/user";
import type { User } from "@/types/auth";

export const usersApi = {
  getUsers: async (params?: UserListParams): Promise<PaginatedResponse<User>> => {
    const response = await apiClient.get<PaginatedResponse<User>>(
      API_ENDPOINTS.USERS.BASE,
      { params },
    );
    return response.data;
  },

  getUser: async (id: string): Promise<UserProfile> => {
    const response = await apiClient.get<ApiResponse<UserProfile>>(
      API_ENDPOINTS.USERS.PROFILE(id),
    );
    return response.data.data;
  },

  updateUser: async (id: string, data: UpdateUserRequest): Promise<UserProfile> => {
    const response = await apiClient.patch<ApiResponse<UserProfile>>(
      API_ENDPOINTS.USERS.PROFILE(id),
      data,
    );
    return response.data.data;
  },

  deleteUser: async (id: string): Promise<void> => {
    await apiClient.delete(API_ENDPOINTS.USERS.PROFILE(id));
  },

  updatePreferences: async (preferences: Record<string, unknown>): Promise<void> => {
    await apiClient.put(API_ENDPOINTS.USERS.PREFERENCES, preferences);
  },

  updatePassword: async (data: UpdatePasswordRequest): Promise<void> => {
    await apiClient.put(API_ENDPOINTS.USERS.UPDATE_PASSWORD, data);
  },
};
