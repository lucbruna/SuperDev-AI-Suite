import apiClient from "./client";

// ---------------------------------------------------------------------------
// Verification API client — verificação, geração e execução de código,
// montado em /api/v1/verify (backend/api/v1/verification.py, prefix "/verify").
// ---------------------------------------------------------------------------

const VERIFY_BASE = "/verify";

export interface VerificationResult {
  success?: boolean;
  score?: number;
  findings?: unknown[];
  [key: string]: unknown;
}

export interface CodeGenerationResult {
  code?: string;
  language?: string;
  [key: string]: unknown;
}

export interface CodeExecutionResult {
  stdout?: string;
  stderr?: string;
  exit_code?: number;
  [key: string]: unknown;
}

export interface CodeReviewResult {
  issues?: unknown[];
  summary?: string;
  [key: string]: unknown;
}

export const verificationApi = {
  async verify(input: Record<string, unknown>): Promise<VerificationResult> {
    const { data } = await apiClient.post(`${VERIFY_BASE}/verify`, input);
    return data;
  },

  async generate(input: Record<string, unknown>): Promise<CodeGenerationResult> {
    const { data } = await apiClient.post(`${VERIFY_BASE}/generate`, input);
    return data;
  },

  async execute(input: Record<string, unknown>): Promise<CodeExecutionResult> {
    const { data } = await apiClient.post(`${VERIFY_BASE}/execute`, input);
    return data;
  },

  async review(input: Record<string, unknown>): Promise<CodeReviewResult> {
    const { data } = await apiClient.post(`${VERIFY_BASE}/review`, input);
    return data;
  },
};
