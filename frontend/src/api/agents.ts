import apiClient from '@/api/client';
import type { Agent, AgentMetrics } from '@/types/agent';

export interface AgentTemplate {
  id: string;
  name: string;
  description: string;
  agent_type: string;
  model: string;
  provider: string;
  max_steps: number;
  temperature: number;
  system_prompt: string;
  tools_enabled: string[];
  category: string;
  icon: string;
}

export async function getAgents(): Promise<Agent[]> {
  const { data } = await apiClient.get<Agent[]>('/agents/');
  return data;
}

export async function getAgent(id: string): Promise<Agent> {
  const { data } = await apiClient.get<Agent>(`/agents/${id}`);
  return data;
}

export async function createAgent(agent: {
  name: string;
  description?: string;
  agent_type?: string;
  model?: string;
  provider?: string;
  max_steps?: number;
  temperature?: number;
  system_prompt?: string;
  tools_enabled?: string[];
  template_id?: string;
}): Promise<Agent> {
  const { data } = await apiClient.post<Agent>('/agents/', agent);
  return data;
}

export async function updateAgent(id: string, agent: Partial<{
  name: string;
  description: string;
  model: string;
  provider: string;
  max_steps: number;
  temperature: number;
  system_prompt: string;
  tools_enabled: string[];
}>): Promise<Agent> {
  const { data } = await apiClient.put<Agent>(`/agents/${id}`, agent);
  return data;
}

export async function deleteAgent(id: string): Promise<void> {
  await apiClient.delete(`/agents/${id}`);
}

export async function startAgent(id: string): Promise<Agent> {
  const { data } = await apiClient.post<Agent>(`/agents/${id}/start`);
  return data;
}

export async function stopAgent(id: string): Promise<Agent> {
  const { data } = await apiClient.post<Agent>(`/agents/${id}/stop`);
  return data;
}

export async function getAgentTemplates(): Promise<AgentTemplate[]> {
  const { data } = await apiClient.get<AgentTemplate[]>('/agents/templates');
  return data;
}

export async function getAgentLogs(
  id: string,
  params?: { level?: string; search?: string }
): Promise<string[]> {
  const { data } = await apiClient.get<string[]>(`/agents/${id}/logs`, { params });
  return data;
}

export async function getAgentMetrics(id: string): Promise<AgentMetrics> {
  const { data } = await apiClient.get<AgentMetrics>(`/agents/${id}/metrics`);
  return data;
}
