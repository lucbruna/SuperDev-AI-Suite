import apiClient from "./client";

// ---------------------------------------------------------------------------
// Knowledge bases API client — CRUD, ingestão, busca e contexto,
// montado em /api/v1/knowledge (backend/api/v1/knowledge.py).
// Substitui o fetch direto usado em /memory.
// ---------------------------------------------------------------------------

const KNOWLEDGE_BASE = "/knowledge";

export interface KnowledgeBase {
  id?: string;
  name?: string;
  description?: string;
  created_at?: string;
  document_count?: number;
  [key: string]: unknown;
}

export interface KnowledgeDocument {
  id?: string;
  kb_id?: string;
  title?: string;
  [key: string]: unknown;
}

export interface KnowledgeSearchResult {
  [key: string]: unknown;
}

export interface KnowledgeContext {
  [key: string]: unknown;
}

export const knowledgeApi = {
  async list(): Promise<KnowledgeBase[]> {
    const { data } = await apiClient.get(`${KNOWLEDGE_BASE}/knowledge-bases`);
    return data;
  },

  async create(input: { name: string; description?: string }): Promise<KnowledgeBase> {
    const { data } = await apiClient.post(`${KNOWLEDGE_BASE}/knowledge-bases`, input);
    return data;
  },

  async get(kbId: string): Promise<KnowledgeBase> {
    const { data } = await apiClient.get(`${KNOWLEDGE_BASE}/knowledge-bases/${kbId}`);
    return data;
  },

  async remove(kbId: string): Promise<Record<string, unknown>> {
    const { data } = await apiClient.delete(`${KNOWLEDGE_BASE}/knowledge-bases/${kbId}`);
    return data;
  },

  async addDocument(kbId: string, input: Record<string, unknown>): Promise<KnowledgeDocument> {
    const { data } = await apiClient.post(
      `${KNOWLEDGE_BASE}/knowledge-bases/${kbId}/documents`,
      input,
    );
    return data;
  },

  async search(query: string, kbId?: string, limit = 10): Promise<KnowledgeSearchResult> {
    const { data } = await apiClient.post(`${KNOWLEDGE_BASE}/knowledge-bases/search`, {
      query,
      knowledge_base_ids: kbId ? [kbId] : undefined,
      top_k: limit,
    });
    return data;
  },

  async context(query: string, kbIds?: string[], maxTokens = 4000): Promise<KnowledgeContext> {
    const { data } = await apiClient.post(`${KNOWLEDGE_BASE}/knowledge-bases/context`, {
      query,
      knowledge_base_ids: kbIds,
      max_tokens: maxTokens,
    });
    return data;
  },

  async ingestRepo(
    kbId: string,
    repoPath: string,
    opts: { file_patterns?: string[]; exclude_patterns?: string[] } = {},
  ): Promise<{ ingested_files?: number; knowledge_base_id?: string }> {
    const { data } = await apiClient.post(`${KNOWLEDGE_BASE}/knowledge-bases/${kbId}/ingest-repo`, {
      repo_path: repoPath,
      file_patterns: opts.file_patterns,
      exclude_patterns: opts.exclude_patterns,
    });
    return data;
  },

  async similarCode(
    kbId: string,
    codeSnippet: string,
    opts: { language?: string; top_k?: number } = {},
  ): Promise<KnowledgeSearchResult> {
    const { data } = await apiClient.post(
      `${KNOWLEDGE_BASE}/knowledge-bases/${kbId}/similar-code`,
      null,
      {
        params: { code_snippet: codeSnippet, language: opts.language, top_k: opts.top_k ?? 5 },
      },
    );
    return data;
  },

  async stats(): Promise<Record<string, unknown>> {
    const { data } = await apiClient.get(`${KNOWLEDGE_BASE}`);
    return data;
  },
};
