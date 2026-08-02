import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { organizationsApi, withFallback } from '../services/api';
import type { Organization, OrganizationMember, Paginated } from '../types/api';

export const orgKeys = {
  all: ['organizations'] as const,
  list: ['organizations', 'list'] as const,
  my: ['organizations', 'my'] as const,
  detail: (id: string) => ['organizations', 'detail', id] as const,
  members: (id: string) => ['organizations', 'members', id] as const,
};

/** Lista de organizações (defensiva: [] em falha). */
export function useOrganizations() {
  const query = useQuery({
    queryKey: orgKeys.list,
    queryFn: () =>
      withFallback(organizationsApi.list().then((r) => r.data), {
        items: [],
        total: 0,
        page: 1,
        limit: 20,
      }),
  });
  const data = query.data ?? { items: [], total: 0, page: 1, limit: 20 };
  return { ...query, organizations: data.items, total: data.total };
}

export function useMyOrganizations() {
  const query = useQuery({
    queryKey: orgKeys.my,
    queryFn: () =>
      withFallback(organizationsApi.my().then((r) => r.data), {
        items: [],
        total: 0,
        page: 1,
        limit: 20,
      }),
  });
  const data = query.data ?? { items: [], total: 0, page: 1, limit: 20 };
  return { ...query, organizations: data.items, total: data.total };
}

export function useOrganization(id: string | undefined) {
  return useQuery({
    queryKey: orgKeys.detail(id ?? ''),
    queryFn: () => organizationsApi.get(id as string),
    enabled: Boolean(id),
  });
}

export function useOrganizationMembers(orgId: string | undefined) {
  const query = useQuery<Paginated<OrganizationMember>>({
    queryKey: orgKeys.members(orgId ?? ''),
    queryFn: () =>
      withFallback(organizationsApi.members(orgId as string).then((r) => r.data), {
        items: [],
        total: 0,
        page: 1,
        limit: 50,
      }),
    enabled: Boolean(orgId),
  });
  return {
    members: query.data?.items ?? ([] as OrganizationMember[]),
    isLoading: query.isLoading,
    isError: query.isError,
    refetch: query.refetch,
  };
}

export function useCreateOrganization() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: organizationsApi.create,
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: orgKeys.all }),
  });
}

export function useUpdateOrganization() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Organization> }) =>
      organizationsApi.update(id, data),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: orgKeys.all }),
  });
}

export function useDeleteOrganization() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => organizationsApi.delete(id),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: orgKeys.all }),
  });
}
