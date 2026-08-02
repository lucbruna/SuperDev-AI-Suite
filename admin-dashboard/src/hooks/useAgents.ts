import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { agentsApi, withFallback } from '../services/api';
import type { Agent } from '../types/api';

export const agentsKeys = {
  all: ['agents'] as const,
  list: ['agents', 'list'] as const,
  detail: (id: string) => ['agents', 'detail', id] as const,
};

/** Lista de agentes (defensiva: [] em falha). */
export function useAgents() {
  const query = useQuery({
    queryKey: agentsKeys.list,
    queryFn: () => withFallback(agentsApi.list(), []),
  });
  return { ...query, agents: query.data ?? [] };
}

export function useAgent(id: string | undefined) {
  return useQuery({
    queryKey: agentsKeys.detail(id ?? ''),
    queryFn: () => agentsApi.get(id as string),
    enabled: Boolean(id),
  });
}

/** Cria um agente e invalida a lista. */
export function useCreateAgent() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: agentsApi.create,
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: agentsKeys.all }),
  });
}

export function useStartAgent() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => agentsApi.start(id),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: agentsKeys.all }),
  });
}

export function useStopAgent() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => agentsApi.stop(id),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: agentsKeys.all }),
  });
}

export function useExecuteAgent() {
  return useMutation({
    mutationFn: ({ id, input, context }: { id: string; input: string; context?: Record<string, unknown> }) =>
      agentsApi.execute(id, input, context),
  });
}

export function useDeleteAgent() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => agentsApi.delete(id),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: agentsKeys.all }),
  });
}

/** Contagem de agentes ativos (útil para o comando central). */
export function useAgentStats() {
  const { agents } = useAgents();
  const active = agents.filter((a: Agent) => a.status === 'running').length;
  return { total: agents.length, active };
}
