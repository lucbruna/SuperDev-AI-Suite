import { useMutation } from '@tanstack/react-query';
import { searchApi } from '../services/api';
import type { SearchResult } from '../types/api';

export function useSearch() {
  return useMutation({
    mutationFn: ({ query, type, limit }: { query: string; type?: string; limit?: number }) =>
      searchApi.search(query, type, limit),
  });
}

export function useGlobalSearch() {
  const mutation = useSearch();
  return {
    ...mutation,
    results: (mutation.data?.results ?? []) as SearchResult[],
    total: mutation.data?.total ?? 0,
  };
}
