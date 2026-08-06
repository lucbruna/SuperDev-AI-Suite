import apiClient from "./client";

// ---------------------------------------------------------------------------
// Email API client — templates, envio e stats, montado em /api/v1/email
// (backend/email/router.py).
// ---------------------------------------------------------------------------

const EMAIL_BASE = "/email";

export interface EmailTemplate {
  id?: string;
  name?: string;
  subject?: string;
  [key: string]: unknown;
}

export interface EmailStats {
  total_sent?: number;
  failed?: number;
  [key: string]: unknown;
}

export const emailApi = {
  async templates(): Promise<EmailTemplate[]> {
    const { data } = await apiClient.get(`${EMAIL_BASE}/templates`);
    return data;
  },

  async send(input: {
    to: string;
    subject: string;
    template?: string;
    body?: string;
    data?: Record<string, unknown>;
  }): Promise<Record<string, unknown>> {
    const { data } = await apiClient.post(`${EMAIL_BASE}/send`, input);
    return data;
  },

  async stats(): Promise<EmailStats> {
    const { data } = await apiClient.get(`${EMAIL_BASE}/stats`);
    return data;
  },
};
