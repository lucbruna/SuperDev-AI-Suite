import apiClient from "./client";

// ---------------------------------------------------------------------------
// AI Code Knowledge Graph API client — connects the dashboard to the module
// backend mounted at /api/v1/knowledge-graph (see backend/app.py).
// ---------------------------------------------------------------------------

const KNOWLEDGE_GRAPH_BASE = "/knowledge-graph";

// The module router returns the backend envelope { success, data }.
function unwrap<T>(payload: unknown): T {
  if (payload && typeof payload === "object") {
    const obj = payload as { data?: T };
    if ("data" in obj) return obj.data as T;
  }
  return payload as T;
}

export interface KnowledgeScanResult {
  stages?: Array<{
    name?: string;
    files?: number;
    detail?: Record<string, unknown>;
  }>;
  [key: string]: unknown;
}

export interface KnowledgeStatus {
  state?: string;
  last_build?: number | null;
  [key: string]: unknown;
}

export interface KnowledgeSnapshot {
  [key: string]: unknown;
}

export interface KnowledgeFile {
  path?: string;
  language?: string;
  [key: string]: unknown;
}

export interface KnowledgeLanguages {
  [language: string]: number;
}

export interface KnowledgeEntityCounts {
  [kind: string]: number;
}

export const knowledgeGraphApi = {
  async scan(project_root?: string, meta?: Record<string, unknown>): Promise<KnowledgeScanResult> {
    const { data } = await apiClient.post(`${KNOWLEDGE_GRAPH_BASE}/scan`, {
      project_root,
      meta,
    });
    return unwrap<KnowledgeScanResult>(data);
  },

  async status(): Promise<KnowledgeStatus> {
    const { data } = await apiClient.get(`${KNOWLEDGE_GRAPH_BASE}/status`);
    return unwrap<KnowledgeStatus>(data);
  },

  async snapshot(): Promise<KnowledgeSnapshot> {
    const { data } = await apiClient.get(`${KNOWLEDGE_GRAPH_BASE}/snapshot`);
    return unwrap<KnowledgeSnapshot>(data);
  },

  async files(language?: string): Promise<{ files: KnowledgeFile[] }> {
    const { data } = await apiClient.get(`${KNOWLEDGE_GRAPH_BASE}/files`, {
      params: language ? { language } : undefined,
    });
    return unwrap<{ files: KnowledgeFile[] }>(data);
  },

  async entityCounts(): Promise<KnowledgeEntityCounts> {
    const { data } = await apiClient.get(`${KNOWLEDGE_GRAPH_BASE}/entity-counts`);
    return unwrap<KnowledgeEntityCounts>(data);
  },

  async languages(): Promise<KnowledgeLanguages> {
    const { data } = await apiClient.get(`${KNOWLEDGE_GRAPH_BASE}/languages`);
    return unwrap<KnowledgeLanguages>(data);
  },

  async reset(): Promise<{ reset?: boolean }> {
    const { data } = await apiClient.post(`${KNOWLEDGE_GRAPH_BASE}/reset`);
    return unwrap<{ reset?: boolean }>(data);
  },
};
