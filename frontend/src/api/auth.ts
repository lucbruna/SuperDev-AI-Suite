import apiClient, { refreshAccessToken } from "./client";
import { API_ENDPOINTS } from "@/constants/api";
import { useAuthStore } from "@/stores/authStore";
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
    // Uses the shared raw-axios helper (not apiClient) on purpose: going
    // through apiClient would re-enter its response interceptor and loop
    // forever when the refresh endpoint itself answers 401.
    const accessToken = await refreshAccessToken();
    if (!accessToken) {
      throw new Error("Failed to refresh session");
    }
    return {
      accessToken,
      refreshToken: useAuthStore.getState().refreshToken ?? refreshToken,
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
