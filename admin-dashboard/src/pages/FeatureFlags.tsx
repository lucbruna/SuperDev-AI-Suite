import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Flag, Loader2 } from 'lucide-react';
import { featureFlagsApi, withFallback } from '../services/api';
import type { FeatureFlag } from '../types/api';
import { cn } from '../lib/utils';

const FLAG_DESCRIPTIONS: Record<string, string> = {
  knowledge_base: 'Habilita o módulo de base de conhecimento (RAG).',
  plugin_marketplace: 'Exibe o marketplace de plugins no painel.',
  feature_flags: 'Habilita a página de feature flags.',
  new_dashboard: 'Usa o novo command center como visão geral.',
  advanced_analytics: 'Habilita gráficos e métricas avançadas.',
};

const FLAG_ICON_COLOR: Record<string, string> = {
  knowledge_base: 'bg-amber-50 text-amber-600 dark:bg-amber-500/10 dark:text-amber-400',
  plugin_marketplace: 'bg-fuchsia-50 text-fuchsia-600 dark:bg-fuchsia-500/10 dark:text-fuchsia-400',
  feature_flags: 'bg-indigo-50 text-indigo-600 dark:bg-indigo-500/10 dark:text-indigo-400',
  new_dashboard: 'bg-sky-50 text-sky-600 dark:bg-sky-500/10 dark:text-sky-400',
  advanced_analytics: 'bg-emerald-50 text-emerald-600 dark:bg-emerald-500/10 dark:text-emerald-400',
};

/** Página de feature flags — toggle real via API. */
export function FeatureFlags() {
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['feature-flags', 'page'],
    queryFn: () =>
      withFallback(featureFlagsApi.list(), { success: true, flags: [] as FeatureFlag[] }),
    staleTime: 1000 * 30,
  });

  const toggleFlag = useMutation({
    mutationFn: (name: string) => featureFlagsApi.toggle(name),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ['feature-flags'] }),
  });

  const flags = data?.flags ?? [];

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Feature Flags</h1>
          <p className="page-subtitle">Controle a liberação de funcionalidades em tempo real</p>
        </div>
        <span className="badge-info">
          <Flag className="h-3 w-3" /> {flags.filter((f) => f.enabled).length} de {flags.length} ativas
        </span>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="card p-5">
              <div className="skeleton h-4 w-2/3" />
              <div className="skeleton mt-3 h-3 w-1/2" />
            </div>
          ))}
        </div>
      ) : flags.length === 0 ? (
        <div className="card">
          <div className="empty-state">
            <Flag className="h-8 w-8 text-ink-muted" />
            <p className="empty-title">Nenhuma flag cadastrada</p>
            <p className="empty-hint">As flags configuradas no backend aparecerão aqui.</p>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {flags.map((flag) => {
            const iconColor = FLAG_ICON_COLOR[flag.name] ?? 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300';
            const toggling = toggleFlag.isPending && toggleFlag.variables === flag.name;
            return (
              <div key={flag.name} className={cn('card card-hover flex flex-col p-5', !flag.enabled && 'opacity-80')}>
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className={cn('flex h-10 w-10 items-center justify-center rounded-xl', iconColor)}>
                      <Flag className="h-5 w-5" />
                    </div>
                    <div className="min-w-0">
                      <p className="truncate font-semibold text-ink">{flag.name}</p>
                      <p className="text-xs text-ink-muted">feature flag</p>
                    </div>
                  </div>
                  <span className={cn('badge shrink-0', flag.enabled ? 'badge-success' : 'badge-neutral')}>
                    {flag.enabled ? 'Ativa' : 'Inativa'}
                  </span>
                </div>

                <p className="mt-3 flex-1 text-sm text-ink-muted">
                  {flag.description ?? FLAG_DESCRIPTIONS[flag.name] ?? 'Sem descrição.'}
                </p>

                <div className="mt-4 flex items-center justify-between border-t border-line pt-3">
                  <span className="text-xs text-ink-muted">Toggle global</span>
                  <button
                    role="switch"
                    aria-checked={flag.enabled}
                    onClick={() => toggling || toggleFlag.mutate(flag.name)}
                    disabled={toggling}
                    className={cn(
                      'relative h-6 w-11 shrink-0 rounded-full transition-colors duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500',
                      flag.enabled ? 'bg-emerald-500' : 'bg-slate-300 dark:bg-slate-700',
                      toggling && 'cursor-wait opacity-70'
                    )}
                  >
                    {toggling && (
                      <Loader2 className="absolute left-1/2 top-1/2 h-3.5 w-3.5 -translate-x-1/2 -translate-y-1/2 animate-spin text-white" />
                    )}
                    <span
                      className={cn(
                        'absolute left-0.5 top-0.5 h-5 w-5 rounded-full bg-white shadow-sm transition-transform duration-200',
                        flag.enabled && 'translate-x-5'
                      )}
                    />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default FeatureFlags;
