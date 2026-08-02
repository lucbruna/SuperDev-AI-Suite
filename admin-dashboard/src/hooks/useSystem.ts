import { useQuery } from '@tanstack/react-query';
import { systemApi, withFallback } from '../services/api';
import type { DashboardData, HealthReport } from '../types/api';

export const systemKeys = {
  dashboard: ['system', 'dashboard'] as const,
};

const EMPTY_DASHBOARD: DashboardData = {
  kpis: {
    organizations: 0,
    projects: 0,
    workflows: 0,
    agents: 0,
    active_agents: 0,
    knowledge_bases: 0,
    plugins_installed: 0,
    executions_today: 0,
    executions_total: 0,
    success_rate: 0,
    cost_today_usd: 0,
    cost_month_usd: 0,
  },
  health: { status: 'unknown', checks: {} },
  metrics: {
    uptime_seconds: 0,
    total_requests: 0,
    total_errors: 0,
    error_rate_pct: 0,
    requests_by_endpoint: {},
  },
  recent_activity: [],
  system: { version: '—', name: 'SuperDev', api_prefix: '/api/v1' },
};

/** Dados agregados do command center (defensivos: zeros em falha). */
export function useDashboardData() {
  const query = useQuery({
    queryKey: systemKeys.dashboard,
    queryFn: () =>
      withFallback(
        systemApi.dashboard().then((r) => r.data),
        EMPTY_DASHBOARD
      ),
    refetchInterval: 1000 * 60,
  });
  return { ...query, data: query.data ?? EMPTY_DASHBOARD };
}

export function useHealth() {
  const { data } = useDashboardData();
  return (data.health ?? { status: 'unknown', checks: {} }) as HealthReport;
}
