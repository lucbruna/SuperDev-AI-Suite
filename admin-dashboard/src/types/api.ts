// Types de domínio do SuperDev — alinhados com os contratos reais da API v1.

// ── Auth ────────────────────────────────────────────────────────────────

export interface User {
  id: string;
  email: string;
  username: string;
  fullName?: string;
  avatarUrl?: string;
  role?: string;
  isEmailVerified?: boolean;
  createdAt?: string;
  updatedAt?: string;
}

export interface AuthResponseData {
  user: User;
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}

export interface ApiEnvelope<T> {
  success: boolean;
  data: T;
}

// ── Organizations ───────────────────────────────────────────────────────

export interface Organization {
  id: string;
  name: string;
  slug: string;
  description?: string | null;
  plan: string;
  settings?: Record<string, unknown> | null;
  memberCount?: number;
  createdAt?: string | null;
  updatedAt?: string | null;
}

export interface OrganizationMemberUser {
  email?: string | null;
  full_name?: string | null;
}

export interface OrganizationMember {
  id: string;
  user_id: string;
  organization_id: string;
  role: string;
  joinedAt?: string | null;
  user?: OrganizationMemberUser;
}

export interface Paginated<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  pages?: number;
}

// ── Projects ────────────────────────────────────────────────────────────

export interface Project {
  id: string;
  name: string;
  description?: string | null;
  visibility?: string;
  created_at?: string;
  updated_at?: string;
}

export interface ProjectListResponse {
  items: Project[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
  has_next: boolean;
  has_prev: boolean;
}

// ── Workflows ───────────────────────────────────────────────────────────

export interface Workflow {
  workflow_id: string;
  name: string;
  description: string;
  steps: Array<Record<string, unknown>>;
  tags: string[];
}

export interface WorkflowRun {
  id: string;
  workflow_id?: string | null;
  agent_id?: string | null;
  status: string;
  trigger?: string | null;
  triggered_by?: string | null;
  created_at?: string | null;
}

// ── Agents ──────────────────────────────────────────────────────────────

export interface Agent {
  id: string;
  name: string;
  description: string;
  agent_type: string;
  status: string;
  tools: Array<Record<string, unknown>>;
}

export interface AgentExecuteResult {
  execution_id: string;
  agent_id: string;
  output: string;
  steps: Array<Record<string, unknown>>;
  tool_calls: Array<Record<string, unknown>>;
  execution_time_ms: number;
  error?: string | null;
}

// ── Knowledge Base ──────────────────────────────────────────────────────

export interface KnowledgeBase {
  id: string;
  name: string;
  description?: string | null;
  type: string;
  is_public: boolean;
  created_at?: string;
  updated_at?: string;
}

// ── Plugins ─────────────────────────────────────────────────────────────

export interface PluginRegistryEntry {
  name: string;
  slug: string;
  version: string;
  description: string;
  author: string;
  plugin_type: string;
  tags: string[];
  downloads: number;
  rating: number;
  is_official: boolean;
}

export interface PluginInstalled {
  name: string;
  slug: string;
  version: string;
  status: string;
  config: Record<string, unknown>;
}

// ── Feature Flags ───────────────────────────────────────────────────────

export interface FeatureFlag {
  name: string;
  enabled: boolean;
  description?: string;
}

// ── Executions ──────────────────────────────────────────────────────────

export interface ExecutionsStats {
  count: number;
  running: number;
  failed: number;
  success_rate: number;
  by_status: Record<string, number>;
}

// ── Cost ────────────────────────────────────────────────────────────────

export interface CostSummary {
  currency: string;
  total_usd: number;
  month_usd: number;
  today_usd: number;
}

export interface CostUsage {
  total_requests: number;
  total_errors: number;
  error_rate_pct: number;
  total_tokens: number;
  total_cost_usd: number;
  uptime_seconds: number;
}

export interface CostForecast {
  currency: string;
  month_usd: number;
  avg_daily_usd: number;
  projected_month_usd: number;
  trend: 'up' | 'down' | 'flat';
}

// ── Health & Metrics ────────────────────────────────────────────────────

export interface HealthCheckEntry {
  status: string;
  message?: string;
  latency_ms?: number;
}

export interface HealthReport {
  status: string;
  checks: Record<string, HealthCheckEntry>;
}

export interface MetricsSnapshot {
  uptime_seconds: number;
  total_requests: number;
  total_errors: number;
  error_rate_pct: number;
  requests_by_endpoint: Record<string, number>;
}

// ── Dashboard ───────────────────────────────────────────────────────────

export interface DashboardKpis {
  organizations: number;
  projects: number;
  workflows: number;
  agents: number;
  active_agents: number;
  knowledge_bases: number;
  plugins_installed: number;
  executions_today: number;
  executions_total: number;
  success_rate: number;
  cost_today_usd: number;
  cost_month_usd: number;
}

export interface ActivityItem {
  id: string;
  type: string;
  title: string;
  message?: string;
  actor?: string;
  timestamp: string;
}

export interface DashboardData {
  kpis: DashboardKpis;
  health: HealthReport;
  metrics: MetricsSnapshot;
  recent_activity: ActivityItem[];
  system: {
    version: string;
    name: string;
    api_prefix: string;
  };
}

// ── Notifications ───────────────────────────────────────────────────────

export interface AppNotification {
  id: string;
  user_id: string;
  title: string;
  message: string;
  notification_type: string;
  is_read: boolean;
  data: Record<string, unknown>;
  created_at: string;
}

// ── Search ──────────────────────────────────────────────────────────────

export interface SearchResult {
  id: string;
  type: string;
  title: string;
  snippet: string;
  score?: number;
  metadata?: Record<string, unknown>;
}

export interface SearchResponse {
  query: string;
  total: number;
  results: SearchResult[];
}
