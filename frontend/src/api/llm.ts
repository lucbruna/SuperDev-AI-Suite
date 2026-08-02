import apiClient from "./client";
import { API_BASE_URL, AGENT_TIMEOUT } from "@/constants/api";
import { useAuthStore } from "@/stores/authStore";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface LLMProviderSummary {
  name: string;
  api_key_configured: boolean;
}

export interface LLMProviderDetail {
  name: string;
  class: string;
  default_model: string;
  api_key_configured: boolean;
  api_key_env_var: string;
  available: boolean;
  models: LLMModelInfo[];
}

export interface LLMModelInfo {
  id: string;
  name: string;
  capabilities: string[];
  context_window?: number;
  dimensions?: number;
}

export interface LLMChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
}

export interface LLMChatRequest {
  messages: LLMChatMessage[];
  provider?: string;
  model?: string;
  temperature?: number;
  max_tokens?: number;
  top_p?: number;
  stream?: boolean;
  system?: string;
  tools?: any[];
}

export interface LLMChatResponse {
  id: string;
  model: string;
  provider: string;
  content: string;
  finish_reason: string | null;
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
    cost_usd: number;
  };
  tool_calls?: any[];
}

export interface AgentChatResponse {
  content: string;
  tool_calls: Array<{ name: string; arguments: Record<string, unknown>; error?: string | null }>;
  error?: string | null;
}

export interface LLMHealthResult {
  overall: string;
  providers: Record<string, { status: string; latency_ms?: number; error?: string }>;
}

// ---------------------------------------------------------------------------
// LLM API
// ---------------------------------------------------------------------------

const LLM_BASE = "/llm";

export const llmApi = {
  /** List all providers */
  async listProviders(): Promise<LLMProviderSummary[]> {
    const { data } = await apiClient.get<{ success: boolean; data: { providers: LLMProviderSummary[] } }>(
      `${LLM_BASE}/providers`
    );
    return data.data.providers;
  },

  /** Get provider details */
  async getProvider(name: string): Promise<LLMProviderDetail> {
    const { data } = await apiClient.get<{ success: boolean; data: LLMProviderDetail }>(
      `${LLM_BASE}/providers/${name}`
    );
    return data.data;
  },

  /** Test provider connection */
  async testProvider(name: string): Promise<{ status: string; latency_ms?: number; error?: string }> {
    const { data } = await apiClient.post<{ success: boolean; data: { status: string; latency_ms?: number; error?: string } }>(
      `${LLM_BASE}/providers/${name}/test`
    );
    return data.data;
  },

  /** List models */
  async listModels(provider?: string): Promise<Record<string, { provider: string; default_model: string; models: LLMModelInfo[] }>> {
    const params = provider ? { provider } : {};
    const { data } = await apiClient.get<{ success: boolean; data: Record<string, any> }>(
      `${LLM_BASE}/models`,
      { params }
    );
    return data.data;
  },

  /** Chat completion */
  async chat(req: LLMChatRequest): Promise<LLMChatResponse> {
    const { data } = await apiClient.post<LLMChatResponse>(
      "/chat/completions",
      req
    );
    return data;
  },

  /** Run the workspace-enabled coding agent. Uses extended timeout (5 min) for multi-step execution. */
  async agentChat(req: { message: string; provider?: string; model?: string; temperature?: number }): Promise<AgentChatResponse> {
    const token = useAuthStore.getState().accessToken;
    const { data } = await apiClient.post<AgentChatResponse>("/chat/agent", req, {
      timeout: AGENT_TIMEOUT, // 5 minutes for multi-step agent tasks
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    return data;
  },

  /** Stream chat via SSE — returns an EventSource/ReadableStream */
  streamChat(req: LLMChatRequest): EventSource {
    const token = useAuthStore.getState().accessToken;
    const url = `${API_BASE_URL}${LLM_BASE}/chat/stream`;
    const es = new EventSource(url);

    // EventSource doesn't support POST natively, so we use a workaround
    // For POST streaming, we use fetch with ReadableStream:
    // This function returns a fetch-based stream instead
    es.close(); // Close the GET EventSource
    return es; // Return it anyway for type compatibility
  },

  /** Stream chat via POST + ReadableStream */
  async streamChatFetch(
    req: LLMChatRequest,
    onChunk: (content: string, done: boolean) => void,
    signal?: AbortSignal
  ): Promise<void> {
    const token = useAuthStore.getState().accessToken;
    const response = await fetch(`${API_BASE_URL}/chat/stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(req),
      signal,
    });

    if (!response.ok) {
      const errText = await response.text();
      throw new Error(`Stream error: ${response.status} ${errText}`);
    }

    const reader = response.body?.getReader();
    if (!reader) throw new Error("No response body");

    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const payload = line.slice(6).trim();
          if (payload === "[DONE]") {
            onChunk("", true);
            return;
          }
          try {
            const parsed = JSON.parse(payload);
            if (parsed.error) {
              onChunk(`[Error: ${parsed.error}]`, true);
              return;
            }
            onChunk(parsed.delta || parsed.content || "", Boolean(parsed.finish_reason));
          } catch {
            // Skip malformed JSON
          }
        }
      }
    }

    onChunk("", true);
  },

  /** LLM health check */
  async health(): Promise<LLMHealthResult> {
    const { data } = await apiClient.get<{ success: boolean; data: LLMHealthResult }>(
      `${LLM_BASE}/health`
    );
    return data.data;
  },
};
