"use client";

import {
  createContext,
  useCallback,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import type { User, LoginRequest, RegisterRequest, AuthResponse } from "@/types/auth";
import { authApi } from "@/api/auth";
import { useAuthStore } from "@/stores/authStore";

interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  clearError: () => void;
}

export const AuthContext = createContext<AuthContextValue | null>(null);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const { user, isAuthenticated, setUser, setTokens, login: storeLogin, logout: storeLogout } =
    useAuthStore();

  useEffect(() => {
    const token = useAuthStore.getState().accessToken;
    if (token) {
      authApi
        .getMe()
        .then((user) => setUser(user))
        .catch(() => storeLogout())
        .finally(() => setIsLoading(false));
    } else {
      // A profile without tokens can remain from an older local-storage format.
      // It must not unlock protected pages because every API call would be 401.
      storeLogout();
      setIsLoading(false);
    }
  }, [setUser, storeLogout]);

  const login = useCallback(
    async (data: LoginRequest) => {
      setError(null);
      setIsLoading(true);
      try {
        const response: AuthResponse = await authApi.login(data);
        storeLogin(response.user, response.accessToken, response.refreshToken);
      } catch (err) {
        const message = err instanceof Error ? err.message : "Login failed";
        setError(message);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [storeLogin],
  );

  const register = useCallback(
    async (data: RegisterRequest) => {
      setError(null);
      setIsLoading(true);
      try {
        const response: AuthResponse = await authApi.register(data);
        storeLogin(response.user, response.accessToken, response.refreshToken);
      } catch (err) {
        const message = err instanceof Error ? err.message : "Registration failed";
        setError(message);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [storeLogin],
  );

  const logout = useCallback(async () => {
    try {
      await authApi.logout();
    } catch {
      // continue logout even if API call fails
    } finally {
      storeLogout();
    }
  }, [storeLogout]);

  const refreshUser = useCallback(async () => {
    try {
      const user = await authApi.getMe();
      setUser(user);
    } catch {
      storeLogout();
    }
  }, [setUser, storeLogout]);

  const clearError = useCallback(() => setError(null), []);

  const value = useMemo(
    () => ({
      user,
      isAuthenticated,
      isLoading,
      error,
      login,
      register,
      logout,
      refreshUser,
      clearError,
    }),
    [user, isAuthenticated, isLoading, error, login, register, logout, refreshUser, clearError],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
