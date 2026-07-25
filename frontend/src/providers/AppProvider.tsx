"use client";

import { type ReactNode } from "react";
import { QueryProvider } from "./QueryProvider";
import { ThemeProvider } from "./ThemeProvider";
import { AuthProvider } from "@/contexts/AuthContext";
import { WebSocketProvider } from "./WebSocketProvider";
import { ThemeContextProvider } from "@/contexts/ThemeContext";
import { I18nProvider } from "@/i18n/I18nContext";
import { WorkspaceProvider } from "@/contexts/WorkspaceContext";

interface AppProviderProps {
  children: ReactNode;
}

export function AppProvider({ children }: AppProviderProps) {
  return (
    <QueryProvider>
      <ThemeProvider>
        <ThemeContextProvider>
          <AuthProvider>
            <I18nProvider>
              <WebSocketProvider>
                <WorkspaceProvider>
                  {children}
                </WorkspaceProvider>
              </WebSocketProvider>
            </I18nProvider>
          </AuthProvider>
        </ThemeContextProvider>
      </ThemeProvider>
    </QueryProvider>
  );
}
