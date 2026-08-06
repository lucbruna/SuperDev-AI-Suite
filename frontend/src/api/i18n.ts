import apiClient from "./client";

// ---------------------------------------------------------------------------
// i18n API client — locales e tradução, montado em /api/v1/i18n.
// ---------------------------------------------------------------------------

const I18N_BASE = "/i18n";

export interface I18nLocale {
  code?: string;
  name?: string;
  coverage?: number;
  [key: string]: unknown;
}

export const i18nApi = {
  async locales(): Promise<I18nLocale[]> {
    const { data } = await apiClient.get(`${I18N_BASE}/locales`);
    return data;
  },

  async stats(): Promise<Record<string, unknown>> {
    const { data } = await apiClient.get(`${I18N_BASE}/stats`);
    return data;
  },

  async translate(input: { locale: string; keys: string[] }): Promise<Record<string, string>> {
    const { data } = await apiClient.post(`${I18N_BASE}/translate`, input);
    return data;
  },
};
