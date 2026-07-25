import apiClient from '@/api/client';
import type { Agent, AgentMetrics } from '@/types/agent';

export async function getAgents(): Promise<Agent[]> {
  const { data } = await apiClient.get<Agent[]>('/agents/');
  return data;
}

export async function getAgent(id: string): Promise<Agent> {
  const { data } = await apiClient.get<Agent>(`/agents/${id}`);
  return data;
}

export async function startAgent(id: string): Promise<Agent> {
  const { data } = await apiClient.post<Agent>(`/agents/${id}/start`);
  return data;
}

export async function stopAgent(id: string): Promise<Agent> {
  const { data } = await apiClient.post<Agent>(`/agents/${id}/stop`);
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
