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
  apiKeyConfigured?: boolean;
  models: string[];
  enabled: boolean;
  baseUrl?: string;
}

export interface LLMSettings {
  provider: string;
  model: string;
  temperature: number;
  max_tokens: number;
  system_prompt: string;
}

export interface RuntimeConfig {
  defaultTimeout: number;
  maxMemory: number;
  maxCpu: number;
  sandboxEnabled: boolean;
  allowedLanguages: string[];
  dockerEnabled: boolean;
}

export interface ProjectSettings {
  id: string;
  name: string;
  description: string;
  runtime: string;
  language: string;
  framework: string;
  rootPath: string;
  envVars: Record<string, string>;
  autoSave: boolean;
  lintOnSave: boolean;
}
