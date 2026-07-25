import apiClient from "./client";
import { API_ENDPOINTS } from "@/constants/api";
import type {
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  RefreshTokenResponse,
  User,
} from "@/types/auth";
import type { ApiResponse } from "@/types/api";

export const authApi = {
  login: async (data: LoginRequest): Promise<AuthResponse> => {
    const response = await apiClient.post<ApiResponse<AuthResponse>>(
      API_ENDPOINTS.AUTH.LOGIN,
      data,
    );
    return response.data.data;
  },

  register: async (data: RegisterRequest): Promise<AuthResponse> => {
    const response = await apiClient.post<ApiResponse<AuthResponse>>(
      API_ENDPOINTS.AUTH.REGISTER,
      data,
    );
    return response.data.data;
  },

  logout: async (): Promise<void> => {
    await apiClient.post(API_ENDPOINTS.AUTH.LOGOUT);
  },

  refreshToken: async (refreshToken: string): Promise<RefreshTokenResponse> => {
    const response = await apiClient.post<ApiResponse<RefreshTokenResponse>>(
      API_ENDPOINTS.AUTH.REFRESH,
      { refreshToken },
    );
    return response.data.data;
  },

  getMe: async (): Promise<User> => {
    const response = await apiClient.get<ApiResponse<User>>(
      API_ENDPOINTS.AUTH.ME,
    );
    return response.data.data;
  },
};
