import { useState, useCallback, useEffect } from 'react';
import { Agent, AgentMetrics } from '../types/agent';
import * as agentsApi from '../api/agents';

interface UseAgentsReturn {
  agents: Agent[];
  loading: boolean;
  error: string | null;
  getAgent: (id: string) => Promise<Agent | null>;
  startAgent: (id: string) => Promise<void>;
  stopAgent: (id: string) => Promise<void>;
  getAgentLogs: (id: string, params?: { level?: string; search?: string }) => Promise<string[]>;
  getAgentMetrics: (id: string) => Promise<AgentMetrics | null>;
  refresh: () => Promise<void>;
}

export function useAgents(): UseAgentsReturn {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await agentsApi.getAgents();
      setAgents(data);
    } catch (err: any) {
      setError(err?.message || 'Failed to load agents');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const getAgent = useCallback(async (id: string): Promise<Agent | null> => {
    setError(null);
    try {
      return await agentsApi.getAgent(id);
    } catch (err: any) {
      setError(err?.message || 'Failed to load agent');
      return null;
    }
  }, []);

  const startAgent = useCallback(async (id: string) => {
    setError(null);
    try {
      const updated = await agentsApi.startAgent(id);
      setAgents((prev) => prev.map((a) => (a.id === id ? updated : a)));
    } catch (err: any) {
      setError(err?.message || 'Failed to start agent');
    }
  }, []);

  const stopAgent = useCallback(async (id: string) => {
    setError(null);
    try {
      const updated = await agentsApi.stopAgent(id);
      setAgents((prev) => prev.map((a) => (a.id === id ? updated : a)));
    } catch (err: any) {
      setError(err?.message || 'Failed to stop agent');
    }
  }, []);

  const getAgentLogs = useCallback(
    async (id: string, params?: { level?: string; search?: string }): Promise<string[]> => {
      setError(null);
      try {
        return await agentsApi.getAgentLogs(id, params);
      } catch (err: any) {
        setError(err?.message || 'Failed to load agent logs');
        return [];
      }
    },
    []
  );

  const getAgentMetrics = useCallback(
    async (id: string): Promise<AgentMetrics | null> => {
      setError(null);
      try {
        return await agentsApi.getAgentMetrics(id);
      } catch (err: any) {
        setError(err?.message || 'Failed to load agent metrics');
        return null;
      }
    },
    []
  );

  return {
    agents,
    loading,
    error,
    getAgent,
    startAgent,
    stopAgent,
    getAgentLogs,
    getAgentMetrics,
    refresh,
  };
}
