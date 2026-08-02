import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { projectsApi, withFallback } from '../services/api';
import type { Project } from '../types/api';

export const projectKeys = {
  all: ['projects'] as const,
  list: ['projects', 'list'] as const,
  detail: (id: string) => ['projects', 'detail', id] as const,
};

const EMPTY_LIST = { items: [], total: 0, page: 1, page_size: 20, pages: 1, has_next: false, has_prev: false };

/** Lista de projetos (defensiva: [] em falha). */
export function useProjects() {
  const query = useQuery({
    queryKey: projectKeys.list,
    queryFn: () => withFallback(projectsApi.list(), EMPTY_LIST),
  });
  const data = query.data ?? EMPTY_LIST;
  return { ...query, projects: data.items, total: data.total };
}

export function useProject(id: string | undefined) {
  return useQuery({
    queryKey: projectKeys.detail(id ?? ''),
    queryFn: () => projectsApi.get(id as string),
    enabled: Boolean(id),
  });
}

export function useCreateProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: projectsApi.create,
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: projectKeys.all }),
  });
}

export function useUpdateProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Project> }) =>
      projectsApi.update(id, {
        name: data.name,
        description: data.description ?? undefined,
      }),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: projectKeys.all }),
  });
}

export function useDeleteProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => projectsApi.delete(id),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: projectKeys.all }),
  });
}
