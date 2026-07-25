export interface GeneralSettings {
  defaultLanguage: string;
  timezone: string;
  dateFormat: string;
}

export interface AppearanceSettings {
  theme: "light" | "dark" | "system";
  fontSize: number;
  sidebarPosition: "left" | "right";
  compactMode: boolean;
}

export interface ProviderConfig {
  id: string;
  name: string;
  type: string;
  apiKey: string;
  models: string[];
  enabled: boolean;
  baseUrl?: string;
}

export interface RuntimeConfig {
  defaultTimeout: number;
  maxMemory: number;
  maxCpu: number;
  sandboxEnabled: boolean;
  allowedLanguages: string[];
  dockerEnabled: boolean;
}
