import { useQuery } from '@tanstack/react-query';
import { executionsApi, withFallback } from '../services/api';
import type { ExecutionsStats } from '../types/api';

export const executionsKeys = {
  stats: ['executions', 'stats'] as const,
  list: ['executions', 'list'] as const,
};

const EMPTY_STATS: ExecutionsStats = {
  count: 0,
  running: 0,
  failed: 0,
  success_rate: 0,
  by_status: {},
};

/** Estatísticas de execuções de hoje (defensivas). */
export function useExecutionsStats() {
  const query = useQuery({
    queryKey: executionsKeys.stats,
    queryFn: () =>
      withFallback(
        executionsApi.statsToday().then((r) => r.data),
        EMPTY_STATS
      ),
    refetchInterval: 1000 * 30,
  });
  return { ...query, stats: query.data ?? EMPTY_STATS };
}

/** Execuções recentes (defensivas). */
export function useRecentExecutions(limit = 10) {
  const query = useQuery({
    queryKey: [...executionsKeys.list, limit],
    queryFn: () =>
      withFallback(
        executionsApi.list({ limit }).then((r) => r.data.items),
        []
      ),
  });
  return { ...query, executions: query.data ?? [] };
}
