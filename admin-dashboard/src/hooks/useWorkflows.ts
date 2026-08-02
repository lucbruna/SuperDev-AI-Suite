import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { workflowsApi, withFallback } from '../services/api';
import type { Workflow } from '../types/api';

export const workflowKeys = {
  all: ['workflows'] as const,
  runs: ['workflows', 'runs'] as const,
};

/** Workflows criados via API (defensivo). */
export function useWorkflows() {
  const query = useQuery({
    queryKey: workflowKeys.all,
    queryFn: () => withFallback(workflowsApi.list(), [] as Workflow[]),
  });
  return { ...query, workflows: query.data ?? [] };
}

export function useCreateWorkflow() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: workflowsApi.create,
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: workflowKeys.all }),
  });
}

export function useExecuteWorkflow() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, variables }: { id: string; variables?: Record<string, unknown> }) =>
      workflowsApi.execute(id, variables),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: workflowKeys.runs }),
  });
}
