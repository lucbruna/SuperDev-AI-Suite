export type AgentStatus = 'idle' | 'running' | 'error';

export interface AgentMetrics {
  executions: number;
  avg_latency: number;
  success_rate: number;
}

export interface AgentTool {
  name: string;
  description?: string;
  [key: string]: unknown;
}

export interface Agent {
  id: string;
  name: string;
  description: string;
  agent_type: string;
  status: AgentStatus;
  tools: AgentTool[];
  model: string | null;
  provider: string | null;
  max_steps: number;
  temperature: number;
  system_prompt: string | null;
  template_id: string | null;
}
