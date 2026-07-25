/** Agent status states. */
export const AgentStatus = {
  IDLE: "idle",
  RUNNING: "running",
  PAUSED: "paused",
  ERROR: "error",
  STOPPED: "stopped",
} as const;
export type AgentStatus = (typeof AgentStatus)[keyof typeof AgentStatus];

/** Workflow run status states. */
export const WorkflowRunStatus = {
  PENDING: "pending",
  RUNNING: "running",
  COMPLETED: "completed",
  FAILED: "failed",
  CANCELLED: "cancelled",
  PAUSED: "paused",
} as const;
export type WorkflowRunStatus =
  (typeof WorkflowRunStatus)[keyof typeof WorkflowRunStatus];

/** Chat message roles. */
export const MessageRole = {
  USER: "user",
  ASSISTANT: "assistant",
  SYSTEM: "system",
  TOOL: "tool",
} as const;
export type MessageRole = (typeof MessageRole)[keyof typeof MessageRole];

/** A user in the system. */
export interface User {
  id: string;
  email: string;
  name: string;
  avatarUrl: string | null;
  isActive: boolean;
  createdAt: string | null;
  updatedAt: string | null;
}

/** An organization. */
export interface Organization {
  id: string;
  name: string;
  slug: string;
  plan: string;
  createdAt: string | null;
}

/** A project resource. */
export interface Project {
  id: string;
  name: string;
  description: string;
  organizationId: string;
  status: string;
  createdAt: string | null;
  updatedAt: string | null;
}

/** An AI agent instance. */
export interface Agent {
  id: string;
  name: string;
  type: string;
  status: AgentStatus;
  config: Record<string, unknown>;
  createdAt: string | null;
}

/** An AI model provider. */
export interface Provider {
  id: string;
  name: string;
  type: string;
  isEnabled: boolean;
  config: Record<string, unknown>;
  health: string;
}

/** Provider health check result. */
export interface ProviderHealth {
  providerId: string;
  status: string;
  latencyMs: number;
  lastChecked: string | null;
  error: string | null;
}

/** A plugin. */
export interface Plugin {
  id: string;
  name: string;
  version: string;
  description: string;
  author: string;
  isInstalled: boolean;
  config: Record<string, unknown>;
}

/** A workflow definition. */
export interface Workflow {
  id: string;
  name: string;
  description: string;
  graph: Record<string, unknown>;
  status: string;
  version: number;
  createdAt: string | null;
}

/** A workflow execution run. */
export interface WorkflowRun {
  id: string;
  workflowId: string;
  status: WorkflowRunStatus;
  inputs: Record<string, unknown>;
  outputs: Record<string, unknown>;
  startedAt: string | null;
  finishedAt: string | null;
  error: string | null;
}

/** A single chat message. */
export interface ChatMessage {
  role: MessageRole;
  content: string;
  timestamp: string | null;
  metadata: Record<string, unknown>;
}

/** A complete chat response. */
export interface ChatResponse {
  message: string;
  model: string;
  provider: string;
  usage: Record<string, number>;
  finishReason: string;
}

/** A single streaming chunk. */
export interface StreamingChunk {
  delta: string;
  model: string;
  finishReason: string | null;
  usage: Record<string, number>;
}

/** A conversation thread. */
export interface Conversation {
  id: string;
  title: string;
  messages: ChatMessage[];
  createdAt: string | null;
}

/** An embedding request. */
export interface EmbeddingRequest {
  input: string | string[];
  model: string;
}

/** An embedding response. */
export interface EmbeddingResponse {
  embeddings: number[][];
  model: string;
  usage: Record<string, number>;
}

/** A run-workflow request. */
export interface RunWorkflowRequest {
  workflowId: string;
  inputs: Record<string, unknown>;
  timeout: number;
}

/** A deployment record. */
export interface Deployment {
  id: string;
  projectId: string;
  status: string;
  environment: string;
  url: string | null;
  createdAt: string | null;
}

/** Paginated response wrapper. */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasNext: boolean;
  hasPrevious: boolean;
}

/** Error response from the API. */
export interface ErrorResponse {
  error: string;
  message: string;
  statusCode: number;
  details: Record<string, unknown>;
}

/** An audit log entry. */
export interface AuditLog {
  id: string;
  action: string;
  userId: string;
  resourceType: string;
  resourceId: string;
  details: Record<string, unknown>;
  timestamp: string | null;
}

/** A notification. */
export interface Notification {
  id: string;
  type: string;
  title: string;
  message: string;
  read: boolean;
  createdAt: string | null;
}

/** Login response payload. */
export interface LoginResponse {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
  user: User;
}

/** Query parameters for paginated list endpoints. */
export interface PaginationParams {
  page?: number;
  pageSize?: number;
}
