import { useQuery } from '@tanstack/react-query';
import { costApi, withFallback } from '../services/api';
import type { CostForecast, CostSummary, CostUsage } from '../types/api';

export const costKeys = {
  all: ['cost'] as const,
  summary: ['cost', 'summary'] as const,
  usage: ['cost', 'usage'] as const,
  forecast: ['cost', 'forecast'] as const,
};

const EMPTY_SUMMARY: CostSummary = { currency: 'USD', total_usd: 0, month_usd: 0, today_usd: 0 };
const EMPTY_USAGE: CostUsage = {
  total_requests: 0,
  total_errors: 0,
  error_rate_pct: 0,
  total_tokens: 0,
  total_cost_usd: 0,
  uptime_seconds: 0,
};
const EMPTY_FORECAST: CostForecast = {
  currency: 'USD',
  month_usd: 0,
  avg_daily_usd: 0,
  projected_month_usd: 0,
  trend: 'flat',
};

export function useCostSummary() {
  const query = useQuery({
    queryKey: costKeys.summary,
    queryFn: () =>
      withFallback(
        costApi.summary().then((r) => r.data),
        EMPTY_SUMMARY
      ),
  });
  return { ...query, summary: query.data ?? EMPTY_SUMMARY };
}

export function useCostUsage() {
  const query = useQuery({
    queryKey: costKeys.usage,
    queryFn: () =>
      withFallback(
        costApi.usage().then((r) => r.data),
        EMPTY_USAGE
      ),
  });
  return { ...query, usage: query.data ?? EMPTY_USAGE };
}

export function useCostForecast() {
  const query = useQuery({
    queryKey: costKeys.forecast,
    queryFn: () =>
      withFallback(
        costApi.forecast().then((r) => r.data),
        EMPTY_FORECAST
      ),
  });
  return { ...query, forecast: query.data ?? EMPTY_FORECAST };
}
