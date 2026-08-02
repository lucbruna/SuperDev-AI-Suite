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
    const response = await apiClient.post<{
      access_token: string;
      refresh_token: string;
      token_type: string;
    }>(
      API_ENDPOINTS.AUTH.REFRESH,
      { refresh_token: refreshToken },
    );
    return {
      accessToken: response.data.access_token,
      refreshToken: response.data.refresh_token,
      expiresIn: 0,
    };
  },

  getMe: async (): Promise<User> => {
    const response = await apiClient.get<{ data: { user: User } }>(
      API_ENDPOINTS.AUTH.ME,
    );
    return response.data.data.user;
  },
};
