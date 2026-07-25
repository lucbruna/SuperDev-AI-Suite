// SuperDev TypeScript SDK
// npm install @superdev/sdk

export interface SuperDevConfig {
  baseUrl: string;
  apiKey?: string;
  wsUrl?: string;
  timeout?: number;
}

export interface Project {
  id: string;
  name: string;
  description: string;
  createdAt: string;
  updatedAt: string;
  ownerId: string;
  settings: Record<string, any>;
}

export interface Agent {
  id: string;
  name: string;
  type: string;
  status: string;
  config: Record<string, any>;
}

export interface ChatMessage {
  role: 'system' | 'user' | 'assistant' | 'function';
  content: string;
  name?: string;
  metadata?: Record<string, any>;
}

export interface ChatResponse {
  id: string;
  content: string;
  model: string;
  usage?: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
    estimatedCost?: number;
  };
  finishReason: string;
}

export interface VerificationResult {
  taskId: string;
  success: boolean;
  stage: string;
  finalCode?: string;
  error?: string;
  iterations: number;
  generation?: any;
  execution?: any;
  testing?: any;
  review?: any;
  correction?: any;
}

export interface WorkflowStep {
  id?: string;
  name: string;
  stepType: string;
  config: Record<string, any>;
  dependsOn?: string[];
  maxRetries?: number;
  timeoutSeconds?: number;
  continueOnError?: boolean;
}

export interface Workflow {
  id: string;
  name: string;
  description: string;
  steps: WorkflowStep[];
  variables: Record<string, any>;
  tags: string[];
}

export interface KnowledgeBase {
  id: string;
  name: string;
  description?: string;
  type: string;
  isPublic: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface KnowledgeEntry {
  id: string;
  knowledgeBaseId: string;
  title: string;
  content: string;
  sourceUrl?: string;
  sourceType?: string;
  language?: string;
  tags: string[];
  metadata: Record<string, any>;
}

export interface SearchResult {
  entryId: string;
  chunkId: string;
  title: string;
  content: string;
  similarity: number;
  language?: string;
  tags: string[];
}

export interface Plugin {
  name: string;
  slug: string;
  version: string;
  description: string;
  author: string;
  pluginType: string;
  tags: string[];
  downloads: number;
  rating: number;
  isOfficial: boolean;
}

export interface InstalledPlugin {
  name: string;
  slug: string;
  version: string;
  status: string;
  config: Record<string, any>;
}

export class SuperDevClient {
  private config: SuperDevConfig;
  private client: any;
  private ws: WebSocket | null = null;

  constructor(config?: Partial<SuperDevConfig>) {
    this.config = {
      baseUrl: config?.baseUrl || 'http://localhost:8000',
      apiKey: config?.apiKey || process.env.SUPERDEV_API_KEY,
      wsUrl: config?.wsUrl,
      timeout: config?.timeout || 60000,
    };
  }

  private async request<T>(method: string, path: string, data?: any): Promise<T> {
    const url = `${this.config.baseUrl}${path}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    
    if (this.config.apiKey) {
      headers['Authorization'] = `Bearer ${this.config.apiKey}`;
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);

    try {
      const response = await fetch(url, {
        method,
        headers,
        body: data ? JSON.stringify(data) : undefined,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(`API Error: ${response.status} - ${error.detail || error.message}`);
      }

      return await response.json();
    } catch (error) {
      clearTimeout(timeoutId);
      throw error;
    }
  }

  async healthCheck(): Promise<any> {
    return this.request('GET', '/api/v1/health');
  }

  async getVersion(): Promise<any> {
    return this.request('GET', '/api/v1/version');
  }

  // Projects
  async createProject(name: string, description?: string, template?: string): Promise<Project> {
    const response = await this.request<{ success: boolean; data: Project }>(
      'POST',
      '/api/v1/projects',
      { name, description, template }
    );
    return response.data;
  }

  async listProjects(): Promise<Project[]> {
    const response = await this.request<{ success: boolean; data: Project[] }>('GET', '/api/v1/projects');
    return response.data;
  }

  async getProject(projectId: string): Promise<Project> {
    const response = await this.request<{ success: boolean; data: Project }>('GET', `/api/v1/projects/${projectId}`);
    return response.data;
  }

  async deleteProject(projectId: string): Promise<boolean> {
    await this.request('DELETE', `/api/v1/projects/${projectId}`);
    return true;
  }

  // Agents
  async listAgents(): Promise<Agent[]> {
    const response = await this.request<{ success: boolean; data: Agent[] }>('GET', '/api/v1/agents');
    return response.data;
  }

  async getAgent(agentId: string): Promise<Agent> {
    const response = await this.request<{ success: boolean; data: Agent }>('GET', `/api/v1/agents/${agentId}`);
    return response.data;
  }

  async executeAgentTask(agentId: string, task: string, context?: Record<string, any>): Promise<any> {
    return this.request('POST', `/api/v1/agents/${agentId}/execute`, { task, context });
  }

  // Chat
  async chat(
    messages: ChatMessage[],
    options?: {
      model?: string;
      provider?: string;
      temperature?: number;
      maxTokens?: number;
      stream?: boolean;
    }
  ): Promise<ChatResponse | AsyncGenerator<ChatResponse>> {
    const payload = {
      messages: messages.map(m => ({ role: m.role, content: m.content })),
      model: options?.model,
      provider: options?.provider,
      temperature: options?.temperature ?? 0.7,
      maxTokens: options?.maxTokens ?? 1024,
      stream: options?.stream ?? false,
    };

    if (options?.stream) {
      return this.streamChat(payload);
    }

    const response = await this.request<{ success: boolean; data: ChatResponse }>(
      'POST',
      '/api/v1/chat/completions',
      payload
    );
    return response.data;
  }

  async *streamChat(payload: any): AsyncGenerator<ChatResponse> {
    const response = await fetch(`${this.config.baseUrl}/api/v1/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(this.config.apiKey ? { 'Authorization': `Bearer ${this.config.apiKey}` } : {}),
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`Stream error: ${response.status}`);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) return;

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') return;
            
            try {
              const parsed = JSON.parse(data);
              yield {
                id: parsed.id || '',
                content: parsed.delta || '',
                model: parsed.model || '',
                finishReason: parsed.finish_reason,
              };
            } catch (e) {
              // Ignore parse errors
            }
          }
        }
      }
    } finally {
      reader?.releaseLock();
    }
  }

  // Code Verification
  async verifyCode(params: {
    taskDescription: string;
    language?: string;
    context?: string;
    requirements?: string[];
    existingCode?: string;
    testFiles?: Record<string, string>;
    maxIterations?: number;
    provider?: string;
  }): Promise<VerificationResult> {
    const response = await this.request<{ success: boolean; data: VerificationResult }>(
      'POST',
      '/api/v1/verify',
      params
    );
    return response.data;
  }

  async generateCode(params: {
    prompt: string;
    language?: string;
    context?: string;
    provider?: string;
  }): Promise<any> {
    return this.request('POST', '/api/v1/verify/generate', params);
  }

  async executeCode(code: string, language?: string): Promise<any> {
    return this.request('POST', '/api/v1/verify/execute', { code, language });
  }

  async reviewCode(params: {
    code: string;
    language?: string;
    context?: string;
    provider?: string;
  }): Promise<any> {
    return this.request('POST', '/api/v1/verify/review', params);
  }

  // Workflows
  async createWorkflow(workflow: {
    name: string;
    description: string;
    steps: WorkflowStep[];
    variables?: Record<string, any>;
    tags?: string[];
  }): Promise<Workflow> {
    const response = await this.request<{ success: boolean; data: Workflow }>(
      'POST',
      '/api/v1/workflows',
      workflow
    );
    return response.data;
  }

  async executeWorkflow(workflowId: string, variables?: Record<string, any>): Promise<any> {
    return this.request('POST', `/api/v1/workflows/${workflowId}/execute`, { variables });
  }

  async listWorkflows(tags?: string[]): Promise<Workflow[]> {
    const params = tags ? { tags: tags.join(',') } : undefined;
    const response = await this.request<{ success: boolean; data: Workflow[] }>(
      'GET',
      '/api/v1/workflows',
      params
    );
    return response.data;
  }

  async getWorkflow(workflowId: string): Promise<Workflow> {
    const response = await this.request<{ success: boolean; data: Workflow }>(
      'GET',
      `/api/v1/workflows/${workflowId}`
    );
    return response.data;
  }

  async deleteWorkflow(workflowId: string): Promise<boolean> {
    await this.request('DELETE', `/api/v1/workflows/${workflowId}`);
    return true;
  }

  // Knowledge Base
  async createKnowledgeBase(params: {
    name: string;
    description?: string;
    type?: string;
    isPublic?: boolean;
  }): Promise<KnowledgeBase> {
    const response = await this.request<{ success: boolean; data: KnowledgeBase }>(
      'POST',
      '/api/v1/knowledge-bases',
      params
    );
    return response.data;
  }

  async addDocument(kbId: string, params: {
    title: string;
    content: string;
    sourceUrl?: string;
    sourceType?: string;
    language?: string;
    tags?: string[];
    metadata?: Record<string, any>;
  }): Promise<KnowledgeEntry> {
    const response = await this.request<{ success: boolean; data: KnowledgeEntry }>(
      'POST',
      `/api/v1/knowledge-bases/${kbId}/documents`,
      params
    );
    return response.data;
  }

  async searchKnowledge(params: {
    query: string;
    knowledgeBaseIds?: string[];
    topK?: number;
    similarityThreshold?: number;
  }): Promise<SearchResult[]> {
    const response = await this.request<{ success: boolean; data: SearchResult[] }>(
      'POST',
      '/api/v1/knowledge-bases/search',
      params
    );
    return response.data;
  }

  async getContext(params: {
    query: string;
    knowledgeBaseIds?: string[];
    maxTokens?: number;
  }): Promise<{ context: string; totalTokens: number }> {
    return this.request('POST', '/api/v1/knowledge-bases/context', params);
  }

  async ingestRepository(kbId: string, params: {
    repoPath: string;
    filePatterns?: string[];
    excludePatterns?: string[];
  }): Promise<any> {
    return this.request('POST', `/api/v1/knowledge-bases/${kbId}/ingest-repo`, params);
  }

  async findSimilarCode(params: {
    codeSnippet: string;
    language?: string;
    knowledgeBaseIds?: string[];
    topK?: number;
  }): Promise<SearchResult[]> {
    const response = await this.request<{ success: boolean; data: SearchResult[] }>(
      'POST',
      '/api/v1/knowledge-bases/similar-code',
      params
    );
    return response.data;
  }

  // Plugins
  async listPlugins(params?: {
    pluginType?: string;
    tag?: string;
    search?: string;
  }): Promise<Plugin[]> {
    const response = await this.request<Plugin[]>('GET', '/api/v1/plugins/registry', params);
    return response;
  }

  async installPlugin(slug: string): Promise<any> {
    return this.request('POST', '/api/v1/plugins/install', { slug });
  }

  async uninstallPlugin(slug: string): Promise<boolean> {
    await this.request('DELETE', `/api/v1/plugins/${slug}`);
    return true;
  }

  async enablePlugin(slug: string): Promise<any> {
    return this.request('POST', `/api/v1/plugins/${slug}/enable`);
  }

  async disablePlugin(slug: string): Promise<any> {
    return this.request('POST', `/api/v1/plugins/${slug}/disable`);
  }

  async updatePluginConfig(slug: string, settings: Record<string, any>): Promise<any> {
    return this.request('PUT', `/api/v1/plugins/${slug}/config`, { settings });
  }

  // WebSocket
  connectWebSocket(projectId?: string): WebSocket {
    const wsUrl = (this.config.wsUrl || this.config.baseUrl.replace('http', 'ws')) + '/api/v1/ws';
    const url = projectId ? `${wsUrl}?project_id=${projectId}` : wsUrl;
    this.ws = new WebSocket(url);
    return this.ws;
  }

  async *subscribeEvents(eventTypes: string[]): AsyncGenerator<any> {
    if (!this.ws) {
      this.connectWebSocket();
    }

    if (!this.ws) throw new Error('WebSocket not connected');

    return null; // TypeScript requires yield
    this.ws.onopen = () => {
      this.ws!.send(JSON.stringify({
        type: 'subscribe',
        events: eventTypes,
      }));
    };

    for await (const message of this.ws) {
      if (message.data) {
        yield JSON.parse(message.data.toString());
      }
    }
  }

  // CLI
  async executeCommand(command: string, params?: Record<string, any>): Promise<any> {
    return this.request('POST', '/api/v1/cli/execute', { command, params });
  }
}

export function createClient(config?: Partial<SuperDevConfig>): SuperDevClient {
  return new SuperDevClient(config);
}

export default SuperDevClient;