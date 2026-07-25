import { create } from "zustand";
import { devtools, persist } from "zustand/middleware";

type Theme = "light" | "dark" | "system";

interface ThemeStore {
  theme: Theme;
  resolvedTheme: "light" | "dark";
  setTheme: (theme: Theme) => void;
  setResolvedTheme: (theme: "light" | "dark") => void;
  toggleTheme: () => void;
}

export const useThemeStore = create<ThemeStore>()(
  devtools(
    persist(
      (set) => ({
        theme: "system",
        resolvedTheme: "dark",

        setTheme: (theme) => set({ theme }),

        setResolvedTheme: (resolvedTheme) => set({ resolvedTheme }),

        toggleTheme: () =>
          set((state) => {
            const newTheme = state.resolvedTheme === "dark" ? "light" : "dark";
            return { theme: newTheme, resolvedTheme: newTheme };
          }),
      }),
      {
        name: "theme-storage",
        partialize: (state) => ({ theme: state.theme }),
      },
    ),
  ),
);
