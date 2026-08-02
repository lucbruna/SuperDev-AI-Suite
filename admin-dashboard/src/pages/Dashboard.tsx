import { useMemo } from 'react';
import { Link } from 'react-router-dom';
import {
  Building2,
  FolderKanban,
  Workflow,
  Bot,
  Activity,
  DollarSign,
  CheckCircle2,
  XCircle,
  TrendingUp,
  Minus,
  ArrowRight,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { useDashboardData } from '../hooks/useSystem';
import { useCostSummary } from '../hooks/useCost';
import { useExecutionsStats, useRecentExecutions } from '../hooks/useExecutions';
import { formatUSD, timeAgo, capitalize } from '../lib/utils';
import { cn } from '../lib/utils';

const STATUS_COLORS: Record<string, string> = {
  success: '#10b981',
  running: '#6366f1',
  failed: '#f43f5e',
  pending: '#f59e0b',
  cancelled: '#94a3b8',
  completed: '#10b981',
};

function statusBadge(status: string) {
  const s = (status ?? '').toLowerCase();
  if (s === 'success' || s === 'completed') return <span className="badge-success">{status}</span>;
  if (s === 'running' || s === 'pending') return <span className="badge-warning">{status}</span>;
  if (s === 'failed' || s === 'cancelled') return <span className="badge-danger">{status}</span>;
  return <span className="badge-neutral">{status}</span>;
}

/** Command center: KPIs, saúde, custo, execuções e atividade recente com dados reais. */
export function Dashboard() {
  const { data: dash, isLoading } = useDashboardData();
  const { summary } = useCostSummary();
  const { stats } = useExecutionsStats();
  const { executions } = useRecentExecutions(8);

  const kpis = dash.kpis;
  const health = dash.health;
  const metrics = dash.metrics;
  const activity = dash.recent_activity;

  const healthStatus = health.status ?? 'unknown';
  const healthOk = healthStatus === 'healthy' || healthStatus === 'ok';

  // Dados para gráficos (reais, defensivos)
  const endpointData = useMemo(
    () =>
      Object.entries(metrics.requests_by_endpoint ?? {})
        .map(([name, count]) => ({ name: name.split('/').filter(Boolean).pop() ?? name, count }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 8),
    [metrics.requests_by_endpoint]
  );

  const statusData = useMemo(
    () =>
      Object.entries(stats.by_status ?? {})
        .map(([name, value]) => ({ name: capitalize(name), value }))
        .filter((d) => d.value > 0),
    [stats.by_status]
  );

  const uptimeText = useMemo(() => {
    const s = metrics.uptime_seconds ?? 0;
    if (s < 3600) return `${Math.floor(s / 60)} min`;
    if (s < 86400) return `${(s / 3600).toFixed(1)} h`;
    return `${(s / 86400).toFixed(1)} d`;
  }, [metrics.uptime_seconds]);

  const trendIcon =
    summary.today_usd > 0 ? (
      <TrendingUp className="h-4 w-4 text-emerald-500" />
    ) : (
      <Minus className="h-4 w-4 text-slate-400" />
    );

  const statCards = [
    {
      label: 'Organizações',
      value: kpis.organizations,
      icon: Building2,
      iconBg: 'bg-indigo-50 text-indigo-600 dark:bg-indigo-500/10 dark:text-indigo-400',
      to: '/organizations',
    },
    {
      label: 'Projetos',
      value: kpis.projects,
      icon: FolderKanban,
      iconBg: 'bg-sky-50 text-sky-600 dark:bg-sky-500/10 dark:text-sky-400',
      to: '/projects',
    },
    {
      label: 'Workflows',
      value: kpis.workflows,
      icon: Workflow,
      iconBg: 'bg-violet-50 text-violet-600 dark:bg-violet-500/10 dark:text-violet-400',
      to: '/workflows',
    },
    {
      label: 'Agentes ativos',
      value: kpis.active_agents,
      icon: Bot,
      iconBg: 'bg-emerald-50 text-emerald-600 dark:bg-emerald-500/10 dark:text-emerald-400',
      to: '/agents',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Cabeçalho */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Visão Geral</h1>
          <p className="page-subtitle">
            Command center do SuperDev · {dash.system?.name ?? 'SuperDev'} v
            {dash.system?.version ?? '—'}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className={cn('badge', healthOk ? 'badge-success' : 'badge-danger')}>
            <span className={cn('h-1.5 w-1.5 rounded-full', healthOk ? 'bg-emerald-500' : 'bg-rose-500')} />
            API {healthOk ? 'saudável' : healthStatus}
          </span>
          <span className="badge-neutral">
            <Activity className="h-3 w-3" /> uptime {uptimeText}
          </span>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {statCards.map((c) => (
          <Link key={c.label} to={c.to} className="stat-card card-hover">
            <div className="flex items-start justify-between">
              <div>
                <p className="stat-label">{c.label}</p>
                <p className="stat-value">
                  {isLoading ? <span className="skeleton inline-block h-8 w-14" /> : c.value}
                </p>
              </div>
              <div className={cn('stat-icon', c.iconBg)}>
                <c.icon className="h-5 w-5" />
              </div>
            </div>
          </Link>
        ))}
      </div>

      {/* Custo + Execuções */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <div className="stat-card">
          <p className="stat-label">Custo hoje</p>
          <div className="mt-2 flex items-center gap-2">
            <DollarSign className="h-5 w-5 text-ink-muted" />
            <p className="stat-value">{formatUSD(summary.today_usd)}</p>
          </div>
        </div>
        <div className="stat-card">
          <p className="stat-label">Custo no mês</p>
          <div className="mt-2 flex items-center gap-2">
            <DollarSign className="h-5 w-5 text-ink-muted" />
            <p className="stat-value">{formatUSD(summary.month_usd)}</p>
          </div>
          <span className="mt-1 inline-flex items-center gap-1 text-xs text-ink-muted">{trendIcon} {summary.currency}</span>
        </div>
        <div className="stat-card">
          <p className="stat-label">Execuções hoje</p>
          <p className="stat-value">{kpis.executions_today}</p>
          <span className="mt-1 inline-block text-xs text-ink-muted">Total: {kpis.executions_total}</span>
        </div>
        <div className="stat-card">
          <p className="stat-label">Taxa de sucesso</p>
          <p className="stat-value">{stats.success_rate?.toFixed(1) ?? '—'}%</p>
          <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800">
            <div
              className="h-full rounded-full bg-emerald-500 transition-all"
              style={{ width: `${Math.min(100, stats.success_rate ?? 0)}%` }}
            />
          </div>
        </div>
      </div>

      {/* Gráficos + Atividade */}
      <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
        <div className="card xl:col-span-2">
          <div className="card-header">
            <h3 className="card-title">Requisições por endpoint</h3>
          </div>
          <div className="p-4">
            {endpointData.length === 0 ? (
              <div className="empty-state">
                <Activity className="h-6 w-6 text-ink-muted" />
                <p className="empty-title">Sem dados de requisições</p>
                <p className="empty-hint">Os endpoints aparecerão aqui após o primeiro uso da API.</p>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={endpointData} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
                  <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#94a3b8' }} interval={0} />
                  <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} allowDecimals={false} />
                  <Tooltip
                    cursor={{ fill: 'rgba(99,102,241,0.06)' }}
                    contentStyle={{ borderRadius: 12, border: '1px solid var(--line)', background: 'var(--surface)' }}
                  />
                  <Bar dataKey="count" fill="#6366f1" radius={[4, 4, 0, 0]} maxBarSize={32} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Execuções por status</h3>
          </div>
          <div className="p-4">
            {statusData.length === 0 ? (
              <div className="empty-state">
                <CheckCircle2 className="h-6 w-6 text-ink-muted" />
                <p className="empty-title">Sem execuções hoje</p>
                <p className="empty-hint">As execuções do dia aparecerão aqui.</p>
              </div>
            ) : (
              <>
                <ResponsiveContainer width="100%" height={180}>
                  <PieChart>
                    <Pie data={statusData} dataKey="value" nameKey="name" innerRadius={48} outerRadius={72} paddingAngle={3}>
                      {statusData.map((entry) => (
                        <Cell key={entry.name} fill={STATUS_COLORS[entry.name.toLowerCase()] ?? '#94a3b8'} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{ borderRadius: 12, border: '1px solid var(--line)', background: 'var(--surface)' }}
                    />
                  </PieChart>
                </ResponsiveContainer>
                <div className="mt-2 flex flex-wrap justify-center gap-3">
                  {statusData.map((entry) => (
                    <span key={entry.name} className="badge-neutral">
                      <span
                        className="h-2 w-2 rounded-full"
                        style={{ background: STATUS_COLORS[entry.name.toLowerCase()] ?? '#94a3b8' }}
                      />
                      {entry.name}: {entry.value}
                    </span>
                  ))}
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Atividade + Execuções recentes */}
      <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Atividade recente</h3>
            <Link to="/workflows" className="flex items-center gap-1 text-xs text-primary-600 hover:text-primary-700">
              Ver tudo <ArrowRight className="h-3 w-3" />
            </Link>
          </div>
          <div className="p-2">
            {activity.length === 0 ? (
              <div className="empty-state">
                <Activity className="h-6 w-6 text-ink-muted" />
                <p className="empty-title">Nenhuma atividade</p>
                <p className="empty-hint">Eventos do sistema aparecerão conforme forem registrados.</p>
              </div>
            ) : (
              activity.slice(0, 8).map((item) => (
                <div key={item.id} className="activity-item">
                  <span
                    className={cn(
                      'mt-1.5 h-2 w-2 shrink-0 rounded-full',
                      item.type === 'error'
                        ? 'bg-rose-500'
                        : item.type === 'success'
                          ? 'bg-emerald-500'
                          : item.type === 'warning'
                            ? 'bg-amber-500'
                            : 'bg-indigo-500'
                    )}
                  />
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-ink">{item.title}</p>
                    {item.message && <p className="truncate text-xs text-ink-muted">{item.message}</p>}
                  </div>
                  <span className="shrink-0 text-[11px] text-ink-muted">{timeAgo(item.timestamp)}</span>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Execuções recentes</h3>
            <span className="badge-neutral">{executions.length} execuções</span>
          </div>
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Workflow</th>
                  <th>Status</th>
                  <th>Trigger</th>
                  <th>Quando</th>
                </tr>
              </thead>
              <tbody>
                {executions.length === 0 ? (
                  <tr>
                    <td colSpan={4}>
                      <div className="empty-state">
                        <XCircle className="h-6 w-6 text-ink-muted" />
                        <p className="empty-title">Sem execuções</p>
                        <p className="empty-hint">Execute um workflow para ver os resultados aqui.</p>
                      </div>
                    </td>
                  </tr>
                ) : (
                  executions.map((run) => (
                    <tr key={run.id}>
                      <td className="font-medium text-ink">{run.workflow_id ?? run.agent_id ?? '—'}</td>
                      <td>{statusBadge(run.status)}</td>
                      <td className="text-ink-muted">{run.trigger ?? 'manual'}</td>
                      <td className="text-ink-muted">{timeAgo(run.created_at)}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
