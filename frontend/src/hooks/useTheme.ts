"use client";

import { useTheme } from "next-themes";
import { useCallback, useMemo } from "react";

export function useThemeToggle() {
  const { theme, setTheme, resolvedTheme, systemTheme } = useTheme();

  const isDark = resolvedTheme === "dark";
  const isLight = resolvedTheme === "light";

  const toggleTheme = useCallback(() => {
    setTheme(isDark ? "light" : "dark");
  }, [isDark, setTheme]);

  return useMemo(
    () => ({
      theme,
      resolvedTheme,
      systemTheme,
      isDark,
      isLight,
      toggleTheme,
      setTheme,
    }),
    [theme, resolvedTheme, systemTheme, isDark, isLight, toggleTheme, setTheme],
  );
}
