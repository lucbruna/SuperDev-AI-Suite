"use client";

import { useState, useMemo } from "react";
import Link from "next/link";
import { DashboardLayout } from "@/components/DashboardLayout";
import { useAuthStore } from "@/stores/authStore";
import { useDashboard } from "@/hooks/useDashboard";
import { Card, CardHeader, CardBody } from "@/components/cards/Card";
import { Badge } from "@/components/badges/Badge";
import { Button } from "@/components/buttons/Button";
import { activityVariant, serviceHealthVariant } from "@/utils/format";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatUSD(n: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(n);
}

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toLocaleString("pt-BR");
}

function formatUptime(seconds: number): string {
  const d = Math.floor(seconds / 86400);
  const h = Math.floor((seconds % 86400) / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  if (d > 0) return `${d}d ${h}h`;
  if (h > 0) return `${h}h ${m}m`;
  return `${m}m`;
}

function timeAgo(iso: string): string {
  const diffMs = Date.now() - new Date(iso).getTime();
  const s = Math.floor(diffMs / 1000);
  if (s < 60) return "agora";
  const m = Math.floor(s / 60);
  if (m < 60) return `${m}min`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h`;
  const d = Math.floor(h / 24);
  return `${d}d`;
}

function greeting(): string {
  const h = new Date().getHours();
  if (h < 12) return "Bom dia";
  if (h < 18) return "Boa tarde";
  return "Boa noite";
}

function formatDate(): string {
  return new Date().toLocaleDateString("pt-BR", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

// ---------------------------------------------------------------------------
// Activity type config
// ---------------------------------------------------------------------------

// Activity type → icon (variants live in format.ts via `activityVariant`).
const activityIcons: Record<string, string> = {
  agent: "🤖",
  workflow: "⚡",
  workflow_run: "⚡",
  project: "📁",
  error: "❌",
  create: "➕",
  update: "✏️",
  delete: "🗑️",
  execute: "▶️",
  auth: "🔒",
};

function getActivityStyle(type: string) {
  for (const [key, icon] of Object.entries(activityIcons)) {
    if (type.toLowerCase().includes(key)) return { icon, variant: activityVariant(key) };
  }
  return { icon: "📋", variant: activityVariant("unknown") };
}

// ---------------------------------------------------------------------------
// AI Modules config
// ---------------------------------------------------------------------------

const aiModules = [
  { name: "Orchestrator", icon: "🎯", color: "bg-indigo-50 text-indigo-600 dark:bg-indigo-950 dark:text-indigo-400", desc: "Coordenação multi-agente" },
  { name: "Data Platform", icon: "📊", color: "bg-cyan-50 text-cyan-600 dark:bg-cyan-950 dark:text-cyan-400", desc: "Ingestão, ML, Analytics" },
  { name: "ERP Operations", icon: "🏭", color: "bg-amber-50 text-amber-600 dark:bg-amber-950 dark:text-amber-400", desc: "Workflow, Estoque, Vendas" },
  { name: "Business Intelligence", icon: "📈", color: "bg-emerald-50 text-emerald-600 dark:bg-emerald-950 dark:text-emerald-400", desc: "Finanças, Previsão, Marketing" },
  { name: "Customer Experience", icon: "👥", color: "bg-rose-50 text-rose-600 dark:bg-rose-950 dark:text-rose-400", desc: "CRM, Sentimento, Suporte" },
  { name: "Verification", icon: "✅", color: "bg-teal-50 text-teal-600 dark:bg-teal-950 dark:text-teal-400", desc: "Validação, Hallucination" },
  { name: "Knowledge Engine", icon: "🧠", color: "bg-violet-50 text-violet-600 dark:bg-violet-950 dark:text-violet-400", desc: "RAG, Embeddings, Cache" },
  { name: "AI Tools", icon: "🔧", color: "bg-orange-50 text-orange-600 dark:bg-orange-950 dark:text-orange-400", desc: "Terminal, Git, HTTP, MCP" },
];

// ---------------------------------------------------------------------------
// Quick actions config
// ---------------------------------------------------------------------------

const quickActions = [
  { label: "Novo Projeto", description: "Criar um novo projeto", icon: "➕", href: "/projects", color: "bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400" },
  { label: "Chat IA", description: "Converse com modelos de IA", icon: "💬", href: "/chat", color: "bg-green-50 text-green-600 dark:bg-green-900/30 dark:text-green-400" },
  { label: "Workflows", description: "Automações e pipelines", icon: "⚡", href: "/workflows", color: "bg-yellow-50 text-yellow-600 dark:bg-yellow-900/30 dark:text-yellow-400" },
  { label: "Agentes", description: "Gerenciar agentes IA", icon: "🤖", href: "/agents", color: "bg-purple-50 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400" },
  { label: "Terminal", description: "Executar comandos", icon: "💻", href: "/runtime", color: "bg-surface-100 text-surface-600 dark:bg-surface-800 dark:text-surface-400" },
  { label: "Configurações", description: "Perfil e preferências", icon: "⚙️", href: "/settings", color: "bg-surface-100 text-surface-600 dark:bg-surface-800 dark:text-surface-400" },
];

// ---------------------------------------------------------------------------
// Skeleton loaders
// ---------------------------------------------------------------------------

function StatSkeleton() {
  return (
    <div className="rounded-xl border border-surface-200 bg-white p-5 shadow-sm dark:border-surface-700 dark:bg-surface-900 animate-pulse">
      <div className="flex items-start justify-between">
        <div className="h-10 w-10 rounded-lg bg-surface-200 dark:bg-surface-700" />
      </div>
      <div className="mt-4 space-y-2">
        <div className="h-8 w-20 rounded bg-surface-200 dark:bg-surface-700" />
        <div className="h-4 w-28 rounded bg-surface-200 dark:bg-surface-700" />
      </div>
    </div>
  );
}

function CardSkeleton({ className }: { className?: string }) {
  return (
    <div className={`rounded-xl border border-surface-200 bg-white p-5 shadow-sm dark:border-surface-700 dark:bg-surface-900 animate-pulse ${className ?? ""}`}>
      <div className="h-5 w-32 rounded bg-surface-200 dark:bg-surface-700 mb-4" />
      <div className="space-y-3">
        <div className="h-4 w-full rounded bg-surface-200 dark:bg-surface-700" />
        <div className="h-4 w-3/4 rounded bg-surface-200 dark:bg-surface-700" />
        <div className="h-4 w-1/2 rounded bg-surface-200 dark:bg-surface-700" />
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// KPI Stat Card
// ---------------------------------------------------------------------------

function KpiCard({
  icon,
  label,
  value,
  href,
  color,
  trend,
}: {
  icon: string;
  label: string;
  value: string | number;
  href: string;
  color: string;
  trend?: { value: string; direction: "up" | "down" | "neutral" };
}) {
  return (
    <Link href={href}>
      <div className="rounded-xl border border-surface-200 bg-white p-5 shadow-sm transition-all hover:shadow-md hover:border-primary-200 dark:border-surface-700 dark:bg-surface-900 dark:hover:border-primary-800 cursor-pointer group h-full">
        <div className="flex items-start justify-between">
          <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${color} text-lg`}>
            {icon}
          </div>
          {trend && (
            <span className={`inline-flex items-center gap-0.5 rounded-full px-2 py-0.5 text-xs font-medium ${
              trend.direction === "up"
                ? "bg-green-50 text-green-600 dark:bg-green-950 dark:text-green-400"
                : trend.direction === "down"
                  ? "bg-red-50 text-red-600 dark:bg-red-950 dark:text-red-400"
                  : "bg-surface-100 text-surface-600 dark:bg-surface-800 dark:text-surface-400"
            }`}>
              {trend.direction === "up" ? "↑" : trend.direction === "down" ? "↓" : "→"}
              {" "}{trend.value}
            </span>
          )}
        </div>
        <div className="mt-4">
          <p className="text-2xl font-bold text-surface-900 dark:text-surface-50 group-hover:text-primary-600 transition-colors">
            {value}
          </p>
          <p className="mt-1 text-sm text-surface-500 dark:text-surface-400">{label}</p>
        </div>
      </div>
    </Link>
  );
}

// ---------------------------------------------------------------------------
// Health Status Indicator
// ---------------------------------------------------------------------------

function HealthDot({ status }: { status: string }) {
  const color =
    status === "healthy"
      ? "bg-green-500"
      : status === "degraded"
        ? "bg-amber-500"
        : status === "unhealthy"
          ? "bg-red-500"
          : "bg-surface-400";
  return <span className={`h-2.5 w-2.5 rounded-full ${color}`} />;
}

// ---------------------------------------------------------------------------
// Mini Sparkline
// ---------------------------------------------------------------------------

function MiniSparkline({ values, color = "#3b82f6" }: { values: number[]; color?: string }) {
  if (values.length < 2) return null;
  const max = Math.max(...values);
  const min = Math.min(...values);
  const range = max - min || 1;
  const w = 80;
  const h = 24;
  const step = w / (values.length - 1);

  const d = values
    .map((v, i) => {
      const x = i * step;
      const y = h - ((v - min) / range) * h;
      return `${i === 0 ? "M" : "L"} ${x} ${y}`;
    })
    .join(" ");

  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} className="overflow-visible">
      <path d={d} fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

// ---------------------------------------------------------------------------
// Main Dashboard Page
// ---------------------------------------------------------------------------

export default function DashboardPage() {
  const { user } = useAuthStore();
  const { data, isLoading, error, refetch } = useDashboard();
  const [refreshing, setRefreshing] = useState(false);

  const handleRefresh = async () => {
    setRefreshing(true);
    await refetch();
    setRefreshing(false);
  };

  // Top endpoints for metrics
  const topEndpoints = useMemo(() => {
    if (!data?.metrics?.requests_by_endpoint) return [];
    return Object.entries(data.metrics.requests_by_endpoint)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 5);
  }, [data]);

  // Health checks list
  const healthChecks = useMemo(() => {
    if (!data?.health?.checks) return [];
    return Object.entries(data.health.checks);
  }, [data]);

  // Loading state
  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-surface-900 dark:text-surface-50">
            {greeting()}, {user?.fullName || user?.email?.split("@")[0] || "Dev"}
          </h1>
          <p className="mt-1 text-surface-500">{formatDate()}</p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 mb-8">
          {Array.from({ length: 4 }).map((_, i) => <StatSkeleton key={i} />)}
        </div>

        <div className="grid gap-6 lg:grid-cols-3 mb-8">
          <CardSkeleton className="lg:col-span-2" />
          <CardSkeleton />
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <CardSkeleton />
          <CardSkeleton />
        </div>
      </DashboardLayout>
    );
  }

  // Error state
  if (error && !data) {
    return (
      <DashboardLayout>
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-surface-900 dark:text-surface-50">
            {greeting()}, {user?.fullName || user?.email?.split("@")[0] || "Dev"}
          </h1>
          <p className="mt-1 text-surface-500">{formatDate()}</p>
        </div>

        <Card>
          <CardBody>
            <div className="text-center py-12">
              <p className="text-lg font-medium text-surface-900 dark:text-surface-50 mb-2">
                Erro ao carregar dashboard
              </p>
              <p className="text-sm text-surface-500 mb-6">
                Não foi possível conectar ao backend. Verifique se o servidor está rodando.
              </p>
              <Button variant="primary" onClick={handleRefresh}>
                Tentar novamente
              </Button>
            </div>
          </CardBody>
        </Card>
      </DashboardLayout>
    );
  }

  const kpis = data?.kpis;
  const health = data?.health;
  const metrics = data?.metrics;
  const activity = data?.recent_activity ?? [];
  const system = data?.system;

  return (
    <DashboardLayout>
      {/* ─── Header ────────────────────────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8 gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-surface-900 dark:text-surface-50">
              {greeting()}, {user?.fullName || user?.email?.split("@")[0] || "Dev"}
            </h1>
            {system && (
              <Badge variant="default" size="sm">
                v{system.version}
              </Badge>
            )}
          </div>
          <p className="mt-1 text-surface-500">{formatDate()}</p>
        </div>
        <div className="flex items-center gap-2">
          {health && (
            <Badge variant={serviceHealthVariant(health.status)} size="sm" dot>
              Sistema {health.status === "healthy" ? "Saudável" : health.status === "degraded" ? "Degradado" : "Com Problemas"}
            </Badge>
          )}
          <Link
            href="/video-studio"
            className="inline-flex items-center gap-2 rounded-lg bg-gradient-to-r from-violet-600 to-fuchsia-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition-all hover:from-violet-700 hover:to-fuchsia-700 hover:shadow-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-violet-500 focus-visible:ring-offset-2"
          >
            🎬 Video Studio
          </Link>
          <Button
            variant="primary"
            size="sm"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            {refreshing ? "..." : "⟳ Atualizar"}
          </Button>
        </div>
      </div>

      {/* ─── KPI Cards ─────────────────────────────────────────────────── */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        <KpiCard
          icon="📁"
          label="Projetos"
          value={kpis?.projects ?? 0}
          href="/projects"
          color="bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400"
        />
        <KpiCard
          icon="🤖"
          label="Agentes IA"
          value={`${kpis?.active_agents ?? 0}/${kpis?.agents ?? 0}`}
          href="/agents"
          color="bg-purple-50 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400"
          trend={kpis?.active_agents ? { value: "ativos", direction: "up" } : undefined}
        />
        <KpiCard
          icon="⚡"
          label="Execuções Hoje"
          value={kpis?.executions_today ?? 0}
          href="/workflows"
          color="bg-amber-50 text-amber-600 dark:bg-amber-900/30 dark:text-amber-400"
          trend={
            kpis?.success_rate
              ? { value: `${kpis.success_rate}% sucesso`, direction: kpis.success_rate >= 90 ? "up" : "down" }
              : undefined
          }
        />
        <KpiCard
          icon="💰"
          label="Custo Mensal"
          value={formatUSD(kpis?.cost_month_usd ?? 0)}
          href="/settings"
          color="bg-emerald-50 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400"
          trend={
            kpis?.cost_today_usd
              ? { value: `${formatUSD(kpis.cost_today_usd)} hoje`, direction: "neutral" }
              : undefined
          }
        />
      </div>

      {/* ─── Main Grid: Activity + Health ───────────────────────────────── */}
      <div className="grid gap-6 lg:grid-cols-3 mb-8">

        {/* ── Activity Feed (2 cols) ── */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
              Atividade Recente
            </h2>
            <Badge variant="default" size="sm">{activity.length} eventos</Badge>
          </CardHeader>
          <CardBody>
            {activity.length === 0 ? (
              <p className="text-center text-sm text-surface-400 py-8">
                Nenhuma atividade recente
              </p>
            ) : (
              <div className="space-y-1 max-h-96 overflow-y-auto pr-1">
                {activity.map((item) => {
                  const style = getActivityStyle(item.type);
                  return (
                    <div
                      key={item.id}
                      className="flex items-start gap-3 rounded-lg p-3 hover:bg-surface-50 dark:hover:bg-surface-800/50 transition-colors"
                    >
                      <span className="text-lg mt-0.5 shrink-0">{style.icon}</span>
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2">
                          <p className="text-sm font-medium text-surface-900 dark:text-surface-50 truncate">
                            {item.title}
                          </p>
                          <Badge variant={style.variant} size="sm">
                            {item.type}
                          </Badge>
                        </div>
                        <p className="text-xs text-surface-500 dark:text-surface-400 truncate mt-0.5">
                          {item.message}
                        </p>
                      </div>
                      <span className="text-xs text-surface-400 whitespace-nowrap shrink-0">
                        {timeAgo(item.timestamp)}
                      </span>
                    </div>
                  );
                })}
              </div>
            )}
          </CardBody>
        </Card>

        {/* ── System Health (1 col) ── */}
        <div className="space-y-6">
          {/* Health Status */}
          <Card>
            <CardHeader>
              <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
                Saúde do Sistema
              </h2>
              {health && <HealthDot status={health.status} />}
            </CardHeader>
            <CardBody>
              <div className="space-y-3">
                {healthChecks.length === 0 ? (
                  <p className="text-sm text-surface-400">Sem verificações disponíveis</p>
                ) : (
                  healthChecks.map(([name, check]) => (
                    <div key={name} className="flex items-center justify-between py-2 border-b border-surface-100 dark:border-surface-800 last:border-0">
                      <div className="flex items-center gap-2 min-w-0">
                        <HealthDot status={check.status} />
                        <span className="text-sm text-surface-700 dark:text-surface-300 truncate capitalize">
                          {name.replace(/_/g, " ")}
                        </span>
                      </div>
                      <div className="flex items-center gap-3 shrink-0">
                        <span className="text-xs text-surface-400">
                          {check.latency_ms}ms
                        </span>
                        <Badge variant={serviceHealthVariant(check.status)} size="sm">
                          {check.status}
                        </Badge>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardBody>
          </Card>

          {/* System Metrics */}
          <Card>
            <CardHeader>
              <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
                Métricas
              </h2>
            </CardHeader>
            <CardBody>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-surface-500">Uptime</span>
                  <span className="text-sm font-semibold text-surface-900 dark:text-surface-50">
                    {formatUptime(metrics?.uptime_seconds ?? 0)}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-surface-500">Requisições</span>
                  <span className="text-sm font-semibold text-surface-900 dark:text-surface-50">
                    {formatNumber(metrics?.total_requests ?? 0)}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-surface-500">Erros</span>
                  <span className="text-sm font-semibold text-surface-900 dark:text-surface-50">
                    {formatNumber(metrics?.total_errors ?? 0)}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-surface-500">Taxa de Erro</span>
                  <span className={`text-sm font-semibold ${(metrics?.error_rate_pct ?? 0) > 5 ? "text-red-600" : "text-green-600"}`}>
                    {(metrics?.error_rate_pct ?? 0).toFixed(2)}%
                  </span>
                </div>

                {topEndpoints.length > 0 && (
                  <>
                    <div className="border-t border-surface-100 dark:border-surface-800 pt-3">
                      <p className="text-xs font-medium text-surface-400 uppercase tracking-wider mb-2">
                        Top Endpoints
                      </p>
                    </div>
                    {topEndpoints.map(([endpoint, count]) => (
                      <div key={endpoint} className="flex items-center justify-between">
                        <span className="text-xs text-surface-500 font-mono truncate max-w-[160px]">
                          {endpoint}
                        </span>
                        <div className="flex items-center gap-2">
                          <div className="w-16 h-1.5 rounded-full bg-surface-100 dark:bg-surface-800 overflow-hidden">
                            <div
                              className="h-full rounded-full bg-primary-500"
                              style={{
                                width: `${Math.min(100, (count / (topEndpoints[0]?.[1] ?? 1)) * 100)}%`,
                              }}
                            />
                          </div>
                          <span className="text-xs font-medium text-surface-700 dark:text-surface-300 w-12 text-right">
                            {formatNumber(count)}
                          </span>
                        </div>
                      </div>
                    ))}
                  </>
                )}
              </div>
            </CardBody>
          </Card>
        </div>
      </div>

      {/* ─── Bottom Section: AI Modules + Quick Actions ─────────────────── */}
      <div className="grid gap-6 lg:grid-cols-3 mb-8">

        {/* ── AI Modules Grid (2 cols) ── */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
              Ecossistema de IA
            </h2>
            <Badge variant="primary" size="sm">{aiModules.length} módulos</Badge>
          </CardHeader>
          <CardBody>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {aiModules.map((mod) => (
                <Link key={mod.name} href="/agents">
                  <div className={`flex flex-col items-center gap-2 p-4 rounded-xl border border-surface-200 dark:border-surface-700 hover:border-primary-300 dark:hover:border-primary-700 transition-all hover:shadow-sm cursor-pointer group`}>
                    <div className={`flex h-12 w-12 items-center justify-center rounded-xl ${mod.color} text-xl group-hover:scale-110 transition-transform`}>
                      {mod.icon}
                    </div>
                    <p className="text-xs font-semibold text-surface-900 dark:text-surface-50 text-center leading-tight">
                      {mod.name}
                    </p>
                    <p className="text-[10px] text-surface-400 text-center leading-tight">
                      {mod.desc}
                    </p>
                  </div>
                </Link>
              ))}
            </div>
          </CardBody>
        </Card>

        {/* ── Quick Actions ── */}
        <Card>
          <CardHeader>
            <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
              Ações Rápidas
            </h2>
          </CardHeader>
          <CardBody>
            <div className="space-y-2">
              {quickActions.map((action) => (
                <Link key={action.label} href={action.href}>
                  <div className="flex items-center gap-3 rounded-lg p-3 hover:bg-surface-50 dark:hover:bg-surface-800/50 transition-colors cursor-pointer group">
                    <div className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg ${action.color} text-sm`}>
                      {action.icon}
                    </div>
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-surface-900 group-hover:text-primary-600 dark:text-surface-50 transition-colors">
                        {action.label}
                      </p>
                      <p className="text-xs text-surface-400 truncate">{action.description}</p>
                    </div>
                    <span className="ml-auto text-surface-300 group-hover:text-primary-500 transition-colors">
                      →
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          </CardBody>
        </Card>
      </div>

      {/* ─── Extra Row: Executions + Cost Summary ────────────────────────── */}
      <div className="grid gap-6 lg:grid-cols-2">

        {/* ── Executions Summary ── */}
        <Card>
          <CardHeader>
            <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
              Execuções
            </h2>
          </CardHeader>
          <CardBody>
            <div className="grid grid-cols-3 gap-4 mb-4">
              <div className="text-center p-3 rounded-lg bg-surface-50 dark:bg-surface-800">
                <p className="text-2xl font-bold text-surface-900 dark:text-surface-50">
                  {kpis?.executions_total ?? 0}
                </p>
                <p className="text-xs text-surface-500 mt-1">Total</p>
              </div>
              <div className="text-center p-3 rounded-lg bg-green-50 dark:bg-green-950/30">
                <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {kpis?.success_rate ?? 0}%
                </p>
                <p className="text-xs text-surface-500 mt-1">Sucesso</p>
              </div>
              <div className="text-center p-3 rounded-lg bg-surface-50 dark:bg-surface-800">
                <p className="text-2xl font-bold text-surface-900 dark:text-surface-50">
                  {kpis?.workflows ?? 0}
                </p>
                <p className="text-xs text-surface-500 mt-1">Workflows</p>
              </div>
            </div>
            <div className="flex items-center gap-2 pt-3 border-t border-surface-100 dark:border-surface-800">
              <span className="text-sm text-surface-500">Conhecimento:</span>
              <Badge variant="primary" size="sm">{kpis?.knowledge_bases ?? 0} bases</Badge>
              <span className="text-sm text-surface-500 ml-2">Plugins:</span>
              <Badge variant="info" size="sm">{kpis?.plugins_installed ?? 0} instalados</Badge>
            </div>
          </CardBody>
        </Card>

        {/* ── Cost Summary ── */}
        <Card>
          <CardHeader>
            <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
              Custos
            </h2>
          </CardHeader>
          <CardBody>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 rounded-lg bg-surface-50 dark:bg-surface-800">
                <div>
                  <p className="text-xs text-surface-500">Hoje</p>
                  <p className="text-xl font-bold text-surface-900 dark:text-surface-50">
                    {formatUSD(kpis?.cost_today_usd ?? 0)}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-surface-500">Este Mês</p>
                  <p className="text-xl font-bold text-primary-600 dark:text-primary-400">
                    {formatUSD(kpis?.cost_month_usd ?? 0)}
                  </p>
                </div>
              </div>

              <div className="space-y-2">
                <p className="text-xs font-medium text-surface-400 uppercase tracking-wider">Distribuição</p>
                <div className="flex items-center gap-3">
                  <div className="flex-1">
                    <div className="w-full h-3 rounded-full bg-surface-100 dark:bg-surface-800 overflow-hidden flex">
                      <div className="h-full bg-primary-500 rounded-l-full" style={{ width: "60%" }} title="Agentes" />
                      <div className="h-full bg-purple-500" style={{ width: "25%" }} title="Workflows" />
                      <div className="h-full bg-amber-500 rounded-r-full" style={{ width: "15%" }} title="LLM" />
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-1.5">
                    <span className="h-2 w-2 rounded-full bg-primary-500" />
                    <span className="text-xs text-surface-500">Agentes 60%</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="h-2 w-2 rounded-full bg-purple-500" />
                    <span className="text-xs text-surface-500">Workflows 25%</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="h-2 w-2 rounded-full bg-amber-500" />
                    <span className="text-xs text-surface-500">LLM 15%</span>
                  </div>
                </div>
              </div>

              <Link href="/settings" className="block">
                <div className="text-center py-2 text-sm text-primary-600 hover:text-primary-700 dark:text-primary-400 font-medium">
                  Ver detalhes →
                </div>
              </Link>
            </div>
          </CardBody>
        </Card>
      </div>
    </DashboardLayout>
  );
}
