import { create } from "zustand";
import { devtools, persist } from "zustand/middleware";
import type { User } from "@/types/auth";

interface AuthStore {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  setUser: (user: User | null) => void;
  setTokens: (accessToken: string, refreshToken: string) => void;
  setLoading: (loading: boolean) => void;
  login: (user: User, accessToken: string, refreshToken: string) => void;
  logout: () => void;
  updateUser: (user: Partial<User>) => void;
}

export const useAuthStore = create<AuthStore>()(
  devtools(
    persist(
      (set) => ({
        user: null,
        accessToken: null,
        refreshToken: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,

        setUser: (user) =>
          set({
            user,
            isAuthenticated: user !== null,
          }),

        setTokens: (accessToken, refreshToken) =>
          set({ accessToken, refreshToken }),

        setLoading: (isLoading) => set({ isLoading }),

        login: (user, accessToken, refreshToken) =>
          set({
            user,
            accessToken,
            refreshToken,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          }),

        logout: () =>
          set({
            user: null,
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,
            isLoading: false,
          }),

        updateUser: (partial) =>
          set((state) => ({
            user: state.user ? { ...state.user, ...partial } : null,
          })),
      }),
      {
        name: "auth-storage",
        partialize: (state) => ({
          accessToken: state.accessToken,
          refreshToken: state.refreshToken,
          user: state.user,
        }),
      },
    ),
  ),
);
