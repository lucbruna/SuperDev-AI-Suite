export type AgentStatus = 'online' | 'offline' | 'busy' | 'error';

export interface AgentMetrics {
  executions: number;
  avg_latency: number;
  success_rate: number;
}

export interface Agent {
  id: string;
  name: string;
  description: string;
  status: AgentStatus;
  capabilities: string[];
  model: string;
  provider: string;
  metrics: AgentMetrics;
  created_at: number;
}
