"use client";

import { createContext, useCallback, useEffect, useMemo, type ReactNode } from "react";
import { useThemeStore } from "@/stores/themeStore";

type Theme = "light" | "dark" | "system";
type ResolvedTheme = "light" | "dark";

interface ThemeContextValue {
  theme: Theme;
  resolvedTheme: ResolvedTheme;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
  isDark: boolean;
  isLight: boolean;
}

export const ThemeContext = createContext<ThemeContextValue | null>(null);

interface ThemeProviderProps {
  children: ReactNode;
  defaultTheme?: Theme;
}

export function ThemeContextProvider({ children, defaultTheme }: ThemeProviderProps) {
  const { theme, resolvedTheme, setTheme, setResolvedTheme, toggleTheme } = useThemeStore();

  const applyTheme = useCallback(
    (resolved: ResolvedTheme) => {
      const root = document.documentElement;
      root.classList.remove("light", "dark");
      root.classList.add(resolved);
      root.style.colorScheme = resolved;
      setResolvedTheme(resolved);
    },
    [setResolvedTheme],
  );

  useEffect(() => {
    if (defaultTheme) {
      setTheme(defaultTheme);
    }
  }, [defaultTheme, setTheme]);

  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");

    const handleChange = () => {
      if (theme === "system") {
        applyTheme(mediaQuery.matches ? "dark" : "light");
      }
    };

    if (theme === "system") {
      applyTheme(mediaQuery.matches ? "dark" : "light");
    } else {
      applyTheme(theme as ResolvedTheme);
    }

    mediaQuery.addEventListener("change", handleChange);
    return () => mediaQuery.removeEventListener("change", handleChange);
  }, [theme, applyTheme]);

  const value = useMemo(
    () => ({
      theme,
      resolvedTheme,
      setTheme,
      toggleTheme,
      isDark: resolvedTheme === "dark",
      isLight: resolvedTheme === "light",
    }),
    [theme, resolvedTheme, setTheme, toggleTheme],
  );

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}
