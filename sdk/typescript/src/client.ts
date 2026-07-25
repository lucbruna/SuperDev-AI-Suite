import { AuthManager } from "./auth";
import {
  ConnectionError,
  throwHttpError,
  TimeoutError,
} from "./errors";
import type {
  Agent,
  ChatResponse,
  Conversation,
  Deployment,
  EmbeddingResponse,
  PaginatedResponse,
  PaginationParams,
  Plugin,
  Project,
  Provider,
  ProviderHealth,
  StreamingChunk,
  User,
  Workflow,
  WorkflowRun,
} from "./types";

/** Configuration for creating a new SuperDevClient. */
export interface SuperDevClientConfig {
  /** Base URL of the SuperDev API (default: http://localhost:8000). */
  baseUrl?: string;
  /** API key for authentication. If omitted, call `login()` before other methods. */
  apiKey?: string;
  /** Default request timeout in milliseconds (default: 30000). */
  timeout?: number;
}

/** Payload for creating a project. */
export interface CreateProjectInput {
  name: string;
  description?: string;
}

/** Payload for updating a project. */
export interface UpdateProjectInput {
  name?: string;
  description?: string;
  status?: string;
}

/** Payload for creating a workflow. */
export interface CreateWorkflowInput {
  name: string;
  description?: string;
  graph: Record<string, unknown>;
}

/** Payload for sending a chat message. */
export interface ChatSendInput {
  message: string;
  model?: string;
  provider?: string;
  conversationId?: string;
  systemPrompt?: string;
}

/** Payload for streaming a chat message. */
export interface ChatStreamInput {
  message: string;
  model?: string;
  provider?: string;
  conversationId?: string;
}

/**
 * Typed, synchronous client for the SuperDev AI Suite API.
 *
 * Uses the Fetch API under the hood. All methods are synchronous with
 * an optional `stream` variant that returns an `AsyncIterable` of
 * {@link StreamingChunk}s.
 *
 * @example
 * ```ts
 * const client = new SuperDevClient({
 *   baseUrl: "http://localhost:8000",
 *   apiKey: "sk-...",
 * });
 *
 * const projects = await client.projects.list();
 * const response = await client.chat.send({ message: "Hello!" });
 * ```
 */
export class SuperDevClient {
  readonly baseUrl: string;
  readonly timeout: number;
  private readonly auth: AuthManager;

  constructor(config: SuperDevClientConfig = {}) {
    this.baseUrl = (config.baseUrl ?? "http://localhost:8000").replace(
      /\/$/,
      "",
    );
    this.timeout = config.timeout ?? 30_000;
    this.auth = new AuthManager({
      apiKey: config.apiKey,
      baseUrl: this.baseUrl,
    });
  }

  // ── Auth ────────────────────────────────────────────────────────

  /**
   * Authenticate with email and password.
   * @returns The authenticated user.
   */
  async login(email: string, password: string): Promise<User> {
    const resp = await this.request<{
      access_token: string;
      refresh_token: string;
      expires_in: number;
      user: User;
    }>("/api/v1/auth/login", { method: "POST", body: { email, password }, auth: false });
    this.auth.setTokens(resp.access_token, resp.refresh_token, resp.expires_in);
    return resp.user;
  }

  /** Clear stored tokens. */
  logout(): void {
    this.auth.clearTokens();
  }

  // ── Resource accessors ──────────────────────────────────────────

  /** User management API. */
  get users(): UserAPI {
    return new UserAPI(this);
  }

  /** Project CRUD API. */
  get projects(): ProjectAPI {
    return new ProjectAPI(this);
  }

  /** Agent control API. */
  get agents(): AgentAPI {
    return new AgentAPI(this);
  }

  /** Workflow management API. */
  get workflows(): WorkflowAPI {
    return new WorkflowAPI(this);
  }

  /** AI provider configuration API. */
  get providers(): ProviderAPI {
    return new ProviderAPI(this);
  }

  /** Plugin management API. */
  get plugins(): PluginAPI {
    return new PluginAPI(this);
  }

  /** Chat and embeddings API. */
  get chat(): ChatAPI {
    return new ChatAPI(this);
  }

  /** Deployment management API. */
  get deployments(): DeploymentAPI {
    return new DeploymentAPI(this);
  }

  // ── Low-level request helpers ───────────────────────────────────

  /** @internal */
  async request<T>(
    path: string,
    opts: {
      method?: string;
      body?: unknown;
      params?: Record<string, unknown>;
      auth?: boolean;
    } = {},
  ): Promise<T> {
    const { method = "GET", body, params, auth = true } = opts;
    let url = `${this.baseUrl}${path}`;

    if (params) {
      const qs = new URLSearchParams();
      for (const [k, v] of Object.entries(params)) {
        if (v != null) qs.set(k, String(v));
      }
      const qsStr = qs.toString();
      if (qsStr) url += `?${qsStr}`;
    }

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    if (auth) {
      Object.assign(headers, this.auth.getHeaders());
    }

    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.timeout);

    let resp: Response;
    try {
      resp = await fetch(url, {
        method,
        headers,
        body: body != null ? JSON.stringify(body) : undefined,
        signal: controller.signal,
      });
    } catch (err) {
      clearTimeout(timer);
      if (err instanceof DOMException && err.name === "AbortError") {
        throw new TimeoutError();
      }
      throw new ConnectionError(
        err instanceof Error ? err.message : "Connection failed",
      );
    }
    clearTimeout(timer);

    if (!resp.ok) {
      let details: Record<string, unknown> = {};
      try {
        details = (await resp.json()) as Record<string, unknown>;
      } catch {
        // ignore
      }
      const message =
        (details["message"] as string) ??
        (details["error"] as string) ??
        resp.statusText;
      throwHttpError(resp.status, message, details);
    }

    const text = await resp.text();
    return (text ? JSON.parse(text) : {}) as T;
  }

  /** @internal */
  async streamRequest(
    path: string,
    body: unknown,
  ): Promise<AsyncIterable<StreamingChunk>> {
    const url = `${this.baseUrl}${path}`;
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    Object.assign(headers, this.auth.getHeaders());

    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.timeout);

    let resp: Response;
    try {
      resp = await fetch(url, {
        method: "POST",
        headers,
        body: JSON.stringify(body),
        signal: controller.signal,
      });
    } catch (err) {
      clearTimeout(timer);
      if (err instanceof DOMException && err.name === "AbortError") {
        throw new TimeoutError();
      }
      throw new ConnectionError(
        err instanceof Error ? err.message : "Connection failed",
      );
    }
    clearTimeout(timer);

    if (!resp.ok) {
      let details: Record<string, unknown> = {};
      try {
        details = (await resp.json()) as Record<string, unknown>;
      } catch {
        // ignore
      }
      const message =
        (details["message"] as string) ??
        (details["error"] as string) ??
        resp.statusText;
      throwHttpError(resp.status, message, details);
    }

    if (!resp.body) {
      throw new Error("Response body is null");
    }

    const reader = resp.body.getReader();
    const decoder = new TextDecoder();

    return {
      [Symbol.asyncIterator]() {
        let done = false;
        return {
          async next() {
            if (done) return { done: true, value: undefined };
            while (true) {
              const { value, done: readerDone } = await reader.read();
              if (readerDone) {
                done = true;
                return { done: true, value: undefined };
              }
              const text = decoder.decode(value, { stream: true });
              const lines = text.split("\n");
              for (const line of lines) {
                const trimmed = line.trim();
                if (!trimmed.startsWith("data: ")) continue;
                const payload = trimmed.slice(6);
                if (payload === "[DONE]") {
                  done = true;
                  return { done: true, value: undefined };
                }
                try {
                  const data = JSON.parse(payload) as Record<string, unknown>;
                  const chunk: StreamingChunk = {
                    delta: (data["delta"] as string) ?? "",
                    model: (data["model"] as string) ?? "",
                    finishReason: (data["finish_reason"] as string) ?? null,
                    usage: (data["usage"] as Record<string, number>) ?? {},
                  };
                  return { done: false, value: chunk };
                } catch {
                  continue;
                }
              }
            }
          },
          async return() {
            reader.releaseLock();
            done = true;
            return { done: true, value: undefined };
          },
        };
      },
    };
  }
}

// ── Resource APIs ────────────────────────────────────────────────

/** User management endpoints. */
export class UserAPI {
  constructor(private readonly client: SuperDevClient) {}

  /** Get the currently authenticated user. */
  async me(): Promise<User> {
    return this.client.request<User>("/api/v1/users/me");
  }

  /** List users with pagination. */
  async list(
    params: PaginationParams = {},
  ): Promise<PaginatedResponse<User>> {
    const data = await this.client.request<{
      items: User[];
      total: number;
      page: number;
      page_size: number;
      has_next: boolean;
      has_previous: boolean;
    }>("/api/v1/users", { params: { page: params.page ?? 1, page_size: params.pageSize ?? 20 } });
    return {
      items: data.items,
      total: data.total,
      page: data.page,
      pageSize: data.page_size,
      hasNext: data.has_next,
      hasPrevious: data.has_previous,
    };
  }
}

/** Project CRUD endpoints. */
export class ProjectAPI {
  constructor(private readonly client: SuperDevClient) {}

  /** List projects with pagination. */
  async list(
    params: PaginationParams = {},
  ): Promise<PaginatedResponse<Project>> {
    const data = await this.client.request<{
      items: Project[];
      total: number;
      page: number;
      page_size: number;
      has_next: boolean;
      has_previous: boolean;
    }>("/api/v1/projects", { params: { page: params.page ?? 1, page_size: params.pageSize ?? 20 } });
    return {
      items: data.items,
      total: data.total,
      page: data.page,
      pageSize: data.page_size,
      hasNext: data.has_next,
      hasPrevious: data.has_previous,
    };
  }

  /** Get a project by ID. */
  async get(projectId: string): Promise<Project> {
    return this.client.request<Project>(`/api/v1/projects/${projectId}`);
  }

  /** Create a new project. */
  async create(input: CreateProjectInput): Promise<Project> {
    return this.client.request<Project>("/api/v1/projects", {
      method: "POST",
      body: input,
    });
  }

  /** Update an existing project. */
  async update(projectId: string, input: UpdateProjectInput): Promise<Project> {
    return this.client.request<Project>(`/api/v1/projects/${projectId}`, {
      method: "PATCH",
      body: input,
    });
  }

  /** Delete a project. */
  async delete(projectId: string): Promise<void> {
    await this.client.request(`/api/v1/projects/${projectId}`, {
      method: "DELETE",
    });
  }
}

/** Agent control endpoints. */
export class AgentAPI {
  constructor(private readonly client: SuperDevClient) {}

  /** List agents with pagination. */
  async list(
    params: PaginationParams = {},
  ): Promise<PaginatedResponse<Agent>> {
    const data = await this.client.request<{
      items: Agent[];
      total: number;
      page: number;
      page_size: number;
      has_next: boolean;
      has_previous: boolean;
    }>("/api/v1/agents", { params: { page: params.page ?? 1, page_size: params.pageSize ?? 20 } });
    return {
      items: data.items,
      total: data.total,
      page: data.page,
      pageSize: data.page_size,
      hasNext: data.has_next,
      hasPrevious: data.has_previous,
    };
  }

  /** Get an agent by ID. */
  async get(agentId: string): Promise<Agent> {
    return this.client.request<Agent>(`/api/v1/agents/${agentId}`);
  }

  /** Start an agent with optional config. */
  async start(
    agentId: string,
    config?: Record<string, unknown>,
  ): Promise<Agent> {
    return this.client.request<Agent>(`/api/v1/agents/${agentId}/start`, {
      method: "POST",
      body: config ?? {},
    });
  }

  /** Stop an agent. */
  async stop(agentId: string): Promise<Agent> {
    return this.client.request<Agent>(`/api/v1/agents/${agentId}/stop`, {
      method: "POST",
    });
  }

  /** Get agent logs. */
  async logs(
    agentId: string,
    limit = 100,
  ): Promise<Record<string, unknown>[]> {
    const data = await this.client.request<{
      logs: Record<string, unknown>[];
    }>(`/api/v1/agents/${agentId}/logs`, { params: { limit } });
    return data.logs;
  }
}

/** Workflow management endpoints. */
export class WorkflowAPI {
  constructor(private readonly client: SuperDevClient) {}

  /** List workflows with pagination. */
  async list(
    params: PaginationParams = {},
  ): Promise<PaginatedResponse<Workflow>> {
    const data = await this.client.request<{
      items: Workflow[];
      total: number;
      page: number;
      page_size: number;
      has_next: boolean;
      has_previous: boolean;
    }>("/api/v1/workflows", { params: { page: params.page ?? 1, page_size: params.pageSize ?? 20 } });
    return {
      items: data.items,
      total: data.total,
      page: data.page,
      pageSize: data.page_size,
      hasNext: data.has_next,
      hasPrevious: data.has_previous,
    };
  }

  /** Get a workflow by ID. */
  async get(workflowId: string): Promise<Workflow> {
    return this.client.request<Workflow>(`/api/v1/workflows/${workflowId}`);
  }

  /** Create a new workflow. */
  async create(input: CreateWorkflowInput): Promise<Workflow> {
    return this.client.request<Workflow>("/api/v1/workflows", {
      method: "POST",
      body: input,
    });
  }

  /** Run a workflow with optional inputs. */
  async run(
    workflowId: string,
    inputs?: Record<string, unknown>,
  ): Promise<WorkflowRun> {
    return this.client.request<WorkflowRun>(
      `/api/v1/workflows/${workflowId}/run`,
      { method: "POST", body: { inputs: inputs ?? {} } },
    );
  }

  /** Get a specific workflow run. */
  async getRun(workflowId: string, runId: string): Promise<WorkflowRun> {
    return this.client.request<WorkflowRun>(
      `/api/v1/workflows/${workflowId}/runs/${runId}`,
    );
  }

  /** Cancel a workflow run. */
  async cancelRun(workflowId: string, runId: string): Promise<WorkflowRun> {
    return this.client.request<WorkflowRun>(
      `/api/v1/workflows/${workflowId}/runs/${runId}/cancel`,
      { method: "POST" },
    );
  }

  /** Delete a workflow. */
  async delete(workflowId: string): Promise<void> {
    await this.client.request(`/api/v1/workflows/${workflowId}`, {
      method: "DELETE",
    });
  }
}

/** AI provider configuration endpoints. */
export class ProviderAPI {
  constructor(private readonly client: SuperDevClient) {}

  /** List all providers. */
  async list(): Promise<Provider[]> {
    const data = await this.client.request<{ items: Provider[] }>(
      "/api/v1/providers",
    );
    return data.items;
  }

  /** Get provider health status. */
  async health(providerId: string): Promise<ProviderHealth> {
    return this.client.request<ProviderHealth>(
      `/api/v1/providers/${providerId}/health`,
    );
  }

  /** Enable a provider. */
  async enable(providerId: string): Promise<Provider> {
    return this.client.request<Provider>(
      `/api/v1/providers/${providerId}/enable`,
      { method: "POST" },
    );
  }

  /** Disable a provider. */
  async disable(providerId: string): Promise<Provider> {
    return this.client.request<Provider>(
      `/api/v1/providers/${providerId}/disable`,
      { method: "POST" },
    );
  }

  /** Configure a provider with new settings. */
  async configure(
    providerId: string,
    config: Record<string, unknown>,
  ): Promise<Provider> {
    return this.client.request<Provider>(
      `/api/v1/providers/${providerId}/config`,
      { method: "PUT", body: config },
    );
  }
}

/** Plugin management endpoints. */
export class PluginAPI {
  constructor(private readonly client: SuperDevClient) {}

  /** List all plugins. */
  async list(): Promise<Plugin[]> {
    const data = await this.client.request<{ items: Plugin[] }>(
      "/api/v1/plugins",
    );
    return data.items;
  }

  /** Install a plugin. */
  async install(pluginId: string): Promise<Plugin> {
    return this.client.request<Plugin>(
      `/api/v1/plugins/${pluginId}/install`,
      { method: "POST" },
    );
  }

  /** Uninstall a plugin. */
  async uninstall(pluginId: string): Promise<void> {
    await this.client.request(`/api/v1/plugins/${pluginId}`, {
      method: "DELETE",
    });
  }

  /** Update a plugin. */
  async update(pluginId: string): Promise<Plugin> {
    return this.client.request<Plugin>(
      `/api/v1/plugins/${pluginId}/update`,
      { method: "POST" },
    );
  }
}

/** Chat and embeddings endpoints. */
export class ChatAPI {
  constructor(private readonly client: SuperDevClient) {}

  /**
   * Send a chat message synchronously.
   * @returns The complete chat response.
   */
  async send(input: ChatSendInput): Promise<ChatResponse> {
    const payload: Record<string, unknown> = { message: input.message };
    if (input.model) payload["model"] = input.model;
    if (input.provider) payload["provider"] = input.provider;
    if (input.conversationId) payload["conversation_id"] = input.conversationId;
    if (input.systemPrompt) payload["system_prompt"] = input.systemPrompt;
    return this.client.request<ChatResponse>("/api/v1/chat", {
      method: "POST",
      body: payload,
    });
  }

  /**
   * Stream a chat message, returning an async iterable of chunks.
   *
   * @example
   * ```ts
   * for await (const chunk of client.chat.stream({ message: "Hi" })) {
   *   process.stdout.write(chunk.delta);
   * }
   * ```
   */
  async stream(input: ChatStreamInput): Promise<AsyncIterable<StreamingChunk>> {
    const payload: Record<string, unknown> = {
      message: input.message,
      stream: true,
    };
    if (input.model) payload["model"] = input.model;
    if (input.provider) payload["provider"] = input.provider;
    if (input.conversationId) payload["conversation_id"] = input.conversationId;
    return this.client.streamRequest("/api/v1/chat", payload);
  }

  /** List all conversations. */
  async conversations(): Promise<Conversation[]> {
    const data = await this.client.request<{ items: Conversation[] }>(
      "/api/v1/chat/conversations",
    );
    return data.items;
  }

  /** Generate embeddings for text input. */
  async embeddings(
    input: string | string[],
    model = "text-embedding-3-small",
  ): Promise<EmbeddingResponse> {
    return this.client.request<EmbeddingResponse>("/api/v1/chat/embeddings", {
      method: "POST",
      body: { input, model },
    });
  }
}

/** Deployment management endpoints. */
export class DeploymentAPI {
  constructor(private readonly client: SuperDevClient) {}

  /** List deployments, optionally filtered by project. */
  async list(projectId?: string): Promise<Deployment[]> {
    const data = await this.client.request<{ items: Deployment[] }>(
      "/api/v1/deployments",
      { params: projectId ? { project_id: projectId } : undefined },
    );
    return data.items;
  }

  /** Get a deployment by ID. */
  async get(deploymentId: string): Promise<Deployment> {
    return this.client.request<Deployment>(
      `/api/v1/deployments/${deploymentId}`,
    );
  }

  /** Create a new deployment. */
  async create(
    projectId: string,
    environment = "production",
  ): Promise<Deployment> {
    return this.client.request<Deployment>("/api/v1/deployments", {
      method: "POST",
      body: { project_id: projectId, environment },
    });
  }

  /** Rollback a deployment. */
  async rollback(deploymentId: string): Promise<Deployment> {
    return this.client.request<Deployment>(
      `/api/v1/deployments/${deploymentId}/rollback`,
      { method: "POST" },
    );
  }
}
