import axios, {
  type AxiosError,
  type AxiosInstance,
  type InternalAxiosRequestConfig,
} from "axios";
import { API_BASE_URL, API_TIMEOUT } from "@/constants/api";
import { useAuthStore } from "@/stores/authStore";

interface RefreshQueueItem {
  resolve: (token: string) => void;
  reject: (error: unknown) => void;
}

/**
 * Attempt to refresh the session using the stored refresh token.
 *
 * Uses the *raw* axios instance on purpose: going through `apiClient` would
 * re-enter this module's own response interceptor and cause an infinite
 * refresh loop whenever the refresh endpoint itself returns 401.
 *
 * This is the single source of truth for token refresh across the app
 * (apiClient, WebSocketProvider and authApi all share it).
 *
 * @returns the new access token, or `null` when refresh is not possible.
 */
export async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = useAuthStore.getState().refreshToken;

  if (!refreshToken) {
    return null;
  }

  try {
    const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
      refresh_token: refreshToken,
    });

    const { access_token, refresh_token } = response.data;
    if (!access_token || !refresh_token) {
      return null;
    }
    useAuthStore.getState().setTokens(access_token, refresh_token);
    return access_token as string;
  } catch {
    return null;
  }
}

class TokenRefreshManager {
  private isRefreshing = false;
  private failedQueue: RefreshQueueItem[] = [];

  private processQueue(error: unknown, token: string | null = null) {
    this.failedQueue.forEach((prom) => {
      if (error) {
        prom.reject(error);
      } else {
        prom.resolve(token!);
      }
    });
    this.failedQueue = [];
  }

  async handle401Error(
    error: AxiosError,
    originalRequest: InternalAxiosRequestConfig & { _retry?: boolean }
  ): Promise<unknown> {
    if (originalRequest._retry) {
      return Promise.reject(error);
    }

    if (this.isRefreshing) {
      return new Promise<string>((resolve, reject) => {
        this.failedQueue.push({ resolve, reject });
      }).then((token) => {
        originalRequest.headers.Authorization = `Bearer ${token}`;
        return apiClient(originalRequest);
      });
    }

    originalRequest._retry = true;
    this.isRefreshing = true;

    try {
      const accessToken = await refreshAccessToken();
      if (!accessToken) {
        // Session cannot be restored — end it for every in-flight request.
        useAuthStore.getState().logout();
        throw new Error("Session expired — unable to refresh access token");
      }
      this.processQueue(null, accessToken);
      originalRequest.headers.Authorization = `Bearer ${accessToken}`;
      return apiClient(originalRequest);
    } catch (refreshError) {
      this.processQueue(refreshError, null);
      return Promise.reject(refreshError);
    } finally {
      this.isRefreshing = false;
    }
  }
}

const tokenRefreshManager = new TokenRefreshManager();

const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = useAuthStore.getState().accessToken;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };

    if (error.response?.status === 401 && !originalRequest._retry) {
      return tokenRefreshManager.handle401Error(error, originalRequest);
    }

    return Promise.reject(error);
  },
);

export default apiClient;
