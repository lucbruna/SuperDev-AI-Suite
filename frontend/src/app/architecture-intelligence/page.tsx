"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { DashboardLayout } from "@/components/DashboardLayout";
import { Card, CardHeader, CardBody } from "@/components/cards/Card";
import { Badge } from "@/components/badges/Badge";
import { Button } from "@/components/buttons/Button";
import { extractErrorMessage } from "@/utils/apiError";
import {
  architectureIntelligenceApi,
  type CheckItem,
  type ForecastItem,
  type InsightItem,
  type PlanTask,
  type Recommendation,
  type SnapshotItem,
  type TrendItem,
} from "@/api/architectureIntelligence";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

type SeverityVariant = "danger" | "warning" | "info" | "default";

const severityVariant = (severity?: string): SeverityVariant => {
  const s = severity?.toLowerCase() ?? "";
  if (s === "critical" || s === "high") return "danger";
  if (s === "medium") return "warning";
  if (s === "low") return "info";
  return "default";
};

const asNum = (v: unknown): number | null =>
  typeof v === "number" && Number.isFinite(v) ? v : null;

const fmtDate = (ts?: number): string =>
  ts ? new Date(ts * 1000).toLocaleString("pt-BR") : "—";

// Compact human summary for an agent result dict (unknown shape).
const agentSummary = (result: unknown): string => {
  if (result == null) return "—";
  if (typeof result === "string") return result;
  if (typeof result === "number" || typeof result === "boolean") return String(result);
  if (Array.isArray(result)) return `${result.length} itens`;
  if (typeof result === "object") {
    const obj = result as Record<string, unknown>;
    const candidate =
      obj.summary ??
      obj.status ??
      obj.title ??
      obj.message ??
      obj.recommendation ??
      obj.detail;
    if (typeof candidate === "string") return candidate;
    const keys = Object.keys(obj);
    return keys.length ? `${keys.length} campos` : "{}";
  }
  return "—";
};

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function ArchitectureIntelligencePage() {
  const [available, setAvailable] = useState(false);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  // Section payloads.
  const [metrics, setMetrics] = useState<Record<string, unknown> | null>(null);
  const [insights, setInsights] = useState<InsightItem[] | null>(null);
  const [plan, setPlan] = useState<{ summary?: string; effort?: Record<string, number>; tasks?: PlanTask[] } | null>(null);
  const [optimizations, setOptimizations] = useState<Recommendation[] | null>(null);
  const [diagnose, setDiagnose] = useState<{ status?: string; checks?: CheckItem[] } | null>(null);
  const [agents, setAgents] = useState<Record<string, unknown> | null>(null);
  const [history, setHistory] = useState<SnapshotItem[] | null>(null);

  // Ask + snapshot interactions.
  const [question, setQuestion] = useState("");
  const [asking, setAsking] = useState(false);
  const [answer, setAnswer] = useState<{ answer?: string; generator?: string } | null>(null);
  const [askError, setAskError] = useState<string | null>(null);
  const [snapshotMsg, setSnapshotMsg] = useState<string | null>(null);
  const [snapshotBusy, setSnapshotBusy] = useState(false);

  const refresh = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const [root, metricsData, insightsData, planData, optData, diagData, agentsData, historyData] =
        await Promise.all([
          architectureIntelligenceApi.report().catch(() => ({ available: false })),
          architectureIntelligenceApi.metrics(),
          architectureIntelligenceApi.insights(),
          architectureIntelligenceApi.plan(),
          architectureIntelligenceApi.optimize(),
          architectureIntelligenceApi.diagnose(),
          architectureIntelligenceApi.agents(),
          architectureIntelligenceApi.history(10),
        ]);
      setAvailable(root.available === true || diagData.status === "ok");
      setMetrics(metricsData);
      setInsights(insightsData.insights ?? null);
      setPlan({
        summary: planData.summary,
        effort: planData.effort,
        tasks: planData.tasks,
      });
      setOptimizations(optData.recommendations ?? null);
      setDiagnose({ status: diagData.status, checks: diagData.checks });
      setAgents(agentsData.agents ?? null);
      setHistory(historyData.snapshots ?? null);
    } catch (e) {
      setLoadError(extractErrorMessage(e, "Falha ao carregar a inteligência de arquitetura"));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const handleAsk = async () => {
    if (!question.trim()) return;
    setAsking(true);
    setAskError(null);
    setAnswer(null);
    try {
      const data = await architectureIntelligenceApi.ask(question.trim());
      setAnswer(data);
    } catch (e) {
      setAskError(extractErrorMessage(e, "Falha ao perguntar"));
    } finally {
      setAsking(false);
    }
  };

  const handleSnapshot = async () => {
    setSnapshotBusy(true);
    setSnapshotMsg(null);
    try {
      const data = await architectureIntelligenceApi.snapshot();
      setSnapshotMsg(
        data.available === false
          ? "Grafo indisponível — snapshot não capturado."
          : data.appended
            ? "Snapshot capturado com sucesso."
            : "Nenhuma alteração desde o último snapshot.",
      );
      const h = await architectureIntelligenceApi.history(10);
      setHistory(h.snapshots ?? null);
    } catch (e) {
      setSnapshotMsg(extractErrorMessage(e, "Falha ao capturar snapshot"));
    } finally {
      setSnapshotBusy(false);
    }
  };

  // Derived view values (defensive).
  const trends: TrendItem[] = (() => {
    const t = metrics?.trends;
    return t && typeof t === "object" && Array.isArray((t as { trends?: unknown }).trends)
      ? ((t as { trends: TrendItem[] }).trends)
      : [];
  })();

  const forecasts: ForecastItem[] = (() => {
    const f = metrics?.forecast;
    return f && typeof f === "object" && Array.isArray((f as { forecasts?: unknown }).forecasts)
      ? ((f as { forecasts: ForecastItem[] }).forecasts)
      : [];
  })();

  const innerInsights: InsightItem[] = (() => {
    const m = metrics?.insights;
    return m && typeof m === "object" && Array.isArray((m as { insights?: unknown }).insights)
      ? ((m as { insights: InsightItem[] }).insights)
      : [];
  })();

  const effortEntries = plan?.effort ? Object.entries(plan.effort) : [];
  const diagnoseStatus = diagnose?.status ?? (available ? "ok" : "degraded");
  const agentEntries = agents ? Object.entries(agents) : [];

  return (
    <DashboardLayout>
      {/* ─── Header ──────────────────────────────────────────────────── */}
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-fuchsia-600 text-2xl shadow-lg">
            🧠
          </div>
          <div>
            <h1 className="text-2xl font-bold text-surface-900 dark:text-surface-50">
              Architecture Intelligence
            </h1>
            <p className="mt-0.5 text-sm text-surface-500">
              Insights, planejamento, previsões e otimização da arquitetura
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant={diagnoseStatus === "ok" ? "success" : "warning"} size="md" dot>
            {loading ? "Carregando…" : diagnoseStatus === "ok" ? "Operacional" : "Degradado"}
          </Badge>
          <Button variant="secondary" size="sm" onClick={refresh} disabled={loading}>
            ⟳ Recarregar
          </Button>
        </div>
      </div>

      {loadError && (
        <div className="mb-6 rounded-lg bg-red-50 px-3 py-2.5 text-sm text-red-600 dark:bg-red-950/40 dark:text-red-400">
          {loadError}
        </div>
      )}

      {/* ─── Snapshot CTA ────────────────────────────────────────────── */}
      <Card className="mb-8">
        <CardBody>
          <div className="flex flex-col items-start justify-between gap-3 sm:flex-row sm:items-center">
            <div>
              <p className="text-sm font-medium text-surface-900 dark:text-surface-50">
                Capturar estado atual
              </p>
              <p className="text-xs text-surface-500">
                Registra um snapshot das métricas no histórico — alimenta tendências e previsões.
              </p>
              {snapshotMsg && (
                <p className="mt-1 text-xs font-medium text-primary-600 dark:text-primary-400">
                  {snapshotMsg}
                </p>
              )}
            </div>
            <Button variant="primary" onClick={handleSnapshot} isLoading={snapshotBusy}>
              📸 Capturar snapshot
            </Button>
          </div>
        </CardBody>
      </Card>

      {/* ─── Trends + Forecast ───────────────────────────────────────── */}
      <div className="mb-8 grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
              Tendências
            </h2>
            <Badge variant="info" size="sm">Histórico</Badge>
          </CardHeader>
          <CardBody>
            {trends.length === 0 ? (
              <p className="py-4 text-center text-sm text-surface-400">
                Sem histórico suficiente ainda (precisa de 2+ snapshots).
              </p>
            ) : (
              <div className="space-y-3">
                {trends.map((t) => (
                  <div
                    key={t.metric ?? t.label}
                    className="flex items-center justify-between rounded-lg border border-surface-100 p-3 dark:border-surface-800"
                  >
                    <div>
                      <p className="text-sm font-medium text-surface-900 dark:text-surface-50">
                        {t.label ?? t.metric ?? "—"}
                      </p>
                      <p className="text-xs text-surface-500">
                        {t.first?.toFixed(1)} → {t.last?.toFixed(1)}
                      </p>
                    </div>
                    <Badge
                      variant={t.direction === "improving" || t.direction === "increasing" ? "success" : t.direction === "declining" ? "danger" : "default"}
                      size="sm"
                    >
                      {t.direction ?? "—"} {t.percent != null ? `· ${t.percent > 0 ? "+" : ""}${t.percent.toFixed(1)}%` : ""}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
              Previsão
            </h2>
            <Badge variant="default" size="sm">Projeção linear</Badge>
          </CardHeader>
          <CardBody>
            {forecasts.length === 0 ? (
              <p className="py-4 text-center text-sm text-surface-400">
                Sem histórico suficiente para prever tendências.
              </p>
            ) : (
              <div className="space-y-3">
                {forecasts.map((f) => (
                  <div
                    key={f.metric}
                    className="flex items-center justify-between rounded-lg border border-surface-100 p-3 dark:border-surface-800"
                  >
                    <div>
                      <p className="text-sm font-medium text-surface-900 dark:text-surface-50">
                        {f.metric ?? "—"}
                      </p>
                      <p className="text-xs text-surface-500">
                        Último valor: {f.last?.toFixed(1)}
                        {f.projected && f.projected.length > 0
                          ? ` · próximo: ${f.projected.map((p) => p.toFixed(1)).join(", ")}`
                          : ""}
                      </p>
                    </div>
                    <Badge
                      variant={f.direction === "up" ? "success" : f.direction === "down" ? "danger" : "default"}
                      size="sm"
                    >
                      {f.direction === "up" ? "▲" : f.direction === "down" ? "▼" : "—"}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </CardBody>
        </Card>
      </div>

      {/* ─── Insights + Plan ─────────────────────────────────────────── */}
      <div className="mb-8 grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
              Insights
            </h2>
            <Badge variant="primary" size="sm">Heurísticas + IA</Badge>
          </CardHeader>
          <CardBody>
            {(insights ?? innerInsights).length === 0 ? (
              <p className="py-4 text-center text-sm text-surface-400">
                Nenhum insight detectado no momento.
              </p>
            ) : (
              <div className="space-y-3">
                {(insights ?? innerInsights).slice(0, 6).map((insight, i) => (
                  <div
                    key={`${insight.category}-${i}`}
                    className="rounded-lg border border-surface-100 p-3 dark:border-surface-800"
                  >
                    <div className="flex items-center gap-2">
                      <Badge variant={severityVariant(insight.severity)} size="sm">
                        {insight.severity ?? "—"}
                      </Badge>
                      {insight.category && (
                        <span className="text-[10px] uppercase tracking-wide text-surface-400">
                          {insight.category}
                        </span>
                      )}
                    </div>
                    <p className="mt-1.5 text-sm font-medium text-surface-900 dark:text-surface-50">
                      {insight.title ?? "Sem título"}
                    </p>
                    {insight.detail && (
                      <p className="mt-0.5 text-xs text-surface-500">{insight.detail}</p>
                    )}
                    {insight.recommendation && (
                      <p className="mt-1.5 text-xs text-primary-600 dark:text-primary-400">
                        💡 {insight.recommendation}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
              Plano de melhoria
            </h2>
            <Badge variant="warning" size="sm">Roadmap</Badge>
          </CardHeader>
          <CardBody>
            {plan?.summary && (
              <p className="mb-3 rounded-lg bg-surface-100 px-3 py-2 text-sm text-surface-700 dark:bg-surface-800 dark:text-surface-300">
                {plan.summary}
              </p>
            )}
            {effortEntries.length > 0 && (
              <div className="mb-3 flex flex-wrap gap-2">
                {effortEntries.map(([effort, count]) => (
                  <Badge key={effort} variant="default" size="sm">
                    Esforço {effort}: {count}
                  </Badge>
                ))}
              </div>
            )}
            {!plan?.tasks || plan.tasks.length === 0 ? (
              <p className="py-4 text-center text-sm text-surface-400">
                Nenhuma ação pendente — arquitetura saudável.
              </p>
            ) : (
              <div className="space-y-3">
                {plan.tasks.slice(0, 8).map((task) => (
                  <div
                    key={task.id ?? task.action}
                    className="rounded-lg border border-surface-100 p-3 dark:border-surface-800"
                  >
                    <div className="flex items-center gap-2">
                      <Badge variant={severityVariant(task.severity)} size="sm">
                        {task.severity ?? "—"}
                      </Badge>
                      {task.category && (
                        <span className="text-[10px] uppercase tracking-wide text-surface-400">
                          {task.category}
                        </span>
                      )}
                      {task.effort && (
                        <span className="ml-auto text-[10px] font-medium text-surface-400">
                          esforço {task.effort}
                        </span>
                      )}
                    </div>
                    <p className="mt-1.5 text-sm font-medium text-surface-900 dark:text-surface-50">
                      {task.action ?? "Sem título"}
                    </p>
                    {task.detail && (
                      <p className="mt-0.5 text-xs text-surface-500">{task.detail}</p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </CardBody>
        </Card>
      </div>

      {/* ─── Optimizations + Diagnostics ─────────────────────────────── */}
      <div className="mb-8 grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
              Otimizações recomendadas
            </h2>
            <Badge variant="success" size="sm">Priorizadas</Badge>
          </CardHeader>
          <CardBody>
            {optimizations === null ? (
              <p className="py-4 text-center text-sm text-surface-400">Carregando…</p>
            ) : optimizations.length === 0 ? (
              <p className="py-4 text-center text-sm text-surface-400">
                Nenhuma otimização recomendada no momento.
              </p>
            ) : (
              <div className="space-y-3">
                {optimizations.slice(0, 6).map((rec, i) => (
                  <div
                    key={`${rec.id ?? rec.category}-${i}`}
                    className="rounded-lg border border-surface-100 p-3 dark:border-surface-800"
                  >
                    <div className="flex items-center gap-2">
                      <Badge variant={severityVariant(rec.priority)} size="sm">
                        {rec.priority ?? "—"}
                      </Badge>
                      {rec.category && (
                        <span className="text-[10px] uppercase tracking-wide text-surface-400">
                          {rec.category}
                        </span>
                      )}
                      {rec.impact && (
                        <span className="ml-auto text-[10px] font-medium text-surface-400">
                          impacto: {rec.impact}
                        </span>
                      )}
                    </div>
                    <p className="mt-1.5 text-sm font-medium text-surface-900 dark:text-surface-50">
                      {rec.action ?? "Sem título"}
                    </p>
                    {rec.detail && (
                      <p className="mt-0.5 text-xs text-surface-500">{rec.detail}</p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
              Diagnóstico
            </h2>
            <Badge variant={diagnoseStatus === "ok" ? "success" : "warning"} size="sm">
              {diagnoseStatus}
            </Badge>
          </CardHeader>
          <CardBody>
            {diagnose?.checks?.length === 0 ? (
              <p className="py-4 text-center text-sm text-surface-400">Carregando…</p>
            ) : (
              <div className="space-y-3">
                {diagnose?.checks?.map((check) => (
                  <div
                    key={check.name}
                    className="flex items-center justify-between rounded-lg border border-surface-100 p-3 dark:border-surface-800"
                  >
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-surface-900 dark:text-surface-50">
                        {check.name}
                      </p>
                      {typeof check.detail === "string" ? (
                        <p className="truncate text-xs text-surface-500">{check.detail}</p>
                      ) : check.detail && typeof check.detail === "object" ? (
                        <p className="truncate text-xs text-surface-500">
                          {JSON.stringify(check.detail)}
                        </p>
                      ) : null}
                    </div>
                    <Badge variant={check.ok ? "success" : "danger"} size="sm" dot>
                      {check.ok ? "ok" : "falha"}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </CardBody>
        </Card>
      </div>

      {/* ─── Agents ──────────────────────────────────────────────────── */}
      <Card className="mb-8">
        <CardHeader>
          <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
            Agentes de inteligência
          </h2>
          <Badge variant="primary" size="sm">{agentEntries.length} agentes</Badge>
        </CardHeader>
        <CardBody>
          {agentEntries.length === 0 ? (
            <p className="py-4 text-center text-sm text-surface-400">
              Nenhum agente disponível.
            </p>
          ) : (
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {agentEntries.map(([name, result]) => (
                <div
                  key={name}
                  className="rounded-lg border border-surface-100 p-3 dark:border-surface-800"
                >
                  <p className="text-sm font-semibold text-surface-900 dark:text-surface-50">
                    {name}
                  </p>
                  <p className="mt-0.5 text-xs text-surface-500">{agentSummary(result)}</p>
                </div>
              ))}
            </div>
          )}
        </CardBody>
      </Card>

      {/* ─── Ask ─────────────────────────────────────────────────────── */}
      <Card className="mb-8">
        <CardHeader>
          <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
            Pergunte sobre a arquitetura
          </h2>
          <Badge variant="default" size="sm">RAG + LLM</Badge>
        </CardHeader>
        <CardBody>
          <div className="flex flex-col gap-2 sm:flex-row">
            <input
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") void handleAsk();
              }}
              placeholder="Ex.: onde está o maior acoplamento?"
              className="w-full rounded-lg border border-surface-300 bg-white px-3 py-2 text-sm text-surface-900 outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 dark:border-surface-600 dark:bg-surface-800 dark:text-surface-100"
            />
            <Button variant="primary" onClick={handleAsk} isLoading={asking} disabled={!question.trim()}>
              Perguntar
            </Button>
          </div>
          {askError && <p className="mt-2 text-xs text-red-500">{askError}</p>}
          {answer?.answer && (
            <div className="mt-4 rounded-lg border border-surface-200 bg-surface-50 p-4 dark:border-surface-700 dark:bg-surface-800/50">
              <div className="mb-1.5 flex items-center gap-2">
                <Badge variant={answer.generator === "llm" ? "primary" : "default"} size="sm">
                  {answer.generator === "llm" ? "Gerado por LLM" : "Resposta heurística"}
                </Badge>
              </div>
              <p className="whitespace-pre-line text-sm text-surface-700 dark:text-surface-300">
                {answer.answer}
              </p>
            </div>
          )}
        </CardBody>
      </Card>

      {/* ─── History ─────────────────────────────────────────────────── */}
      <Card className="mb-8">
        <CardHeader>
          <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
            Histórico de snapshots
          </h2>
          <Badge variant="default" size="sm">{history?.length ?? 0} registros</Badge>
        </CardHeader>
        <CardBody>
          {!history || history.length === 0 ? (
            <p className="py-4 text-center text-sm text-surface-400">
              Nenhum snapshot ainda. Capture o primeiro acima.
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-surface-200 text-xs uppercase tracking-wide text-surface-400 dark:border-surface-700">
                    <th className="pb-2 pr-4 font-medium">Quando</th>
                    <th className="pb-2 pr-4 font-medium">Nós</th>
                    <th className="pb-2 pr-4 font-medium">Arestas</th>
                    <th className="pb-2 pr-4 font-medium">Score</th>
                    <th className="pb-2 font-medium">Problemas</th>
                  </tr>
                </thead>
                <tbody>
                  {history.slice(0, 10).map((snap, i) => (
                    <tr
                      key={`${snap.ts ?? i}-${i}`}
                      className="border-b border-surface-100 last:border-0 dark:border-surface-800"
                    >
                      <td className="py-2.5 pr-4 text-surface-600 dark:text-surface-400">
                        {fmtDate(snap.ts)}
                      </td>
                      <td className="py-2.5 pr-4 tabular-nums text-surface-900 dark:text-surface-50">
                        {asNum(snap.nodes) ?? "—"}
                      </td>
                      <td className="py-2.5 pr-4 tabular-nums text-surface-900 dark:text-surface-50">
                        {asNum(snap.edges) ?? "—"}
                      </td>
                      <td className="py-2.5 pr-4 tabular-nums text-surface-900 dark:text-surface-50">
                        {asNum(snap.score)?.toFixed(1) ?? "—"}
                      </td>
                      <td className="py-2.5 tabular-nums text-surface-900 dark:text-surface-50">
                        {asNum(snap.integrity_issues) ?? "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardBody>
      </Card>

      {/* ─── Back link ───────────────────────────────────────────────── */}
      <div className="mt-6">
        <Link href="/dashboard" className="text-sm text-primary-600 hover:text-primary-700 dark:text-primary-400">
          ← Voltar ao Dashboard
        </Link>
      </div>
    </DashboardLayout>
  );
}
