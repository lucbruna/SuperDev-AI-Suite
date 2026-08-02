import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { knowledgeBaseApi, withFallback } from '../services/api';

export const knowledgeKeys = {
  all: ['knowledge-bases'] as const,
  list: ['knowledge-bases', 'list'] as const,
  detail: (id: string) => ['knowledge-bases', 'detail', id] as const,
};

/** Lista de bases de conhecimento (defensiva: [] em falha). */
export function useKnowledgeBases() {
  const query = useQuery({
    queryKey: knowledgeKeys.list,
    queryFn: () => withFallback(knowledgeBaseApi.list(), []),
  });
  return { ...query, bases: query.data ?? [] };
}

export function useKnowledgeBase(id: string | undefined) {
  return useQuery({
    queryKey: knowledgeKeys.detail(id ?? ''),
    queryFn: () => knowledgeBaseApi.get(id as string),
    enabled: Boolean(id),
  });
}

export function useCreateKnowledgeBase() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: knowledgeBaseApi.create,
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: knowledgeKeys.all }),
  });
}

export function useDeleteKnowledgeBase() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => knowledgeBaseApi.delete(id),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: knowledgeKeys.all }),
  });
}

export function useKnowledgeSearch() {
  return useMutation({
    mutationFn: ({ query, ids }: { query: string; ids?: string[] }) =>
      knowledgeBaseApi.search(query, ids),
  });
}
