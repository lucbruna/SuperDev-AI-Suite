"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { DashboardLayout } from "@/components/DashboardLayout";
import { Card, CardHeader, CardBody } from "@/components/cards/Card";
import { Badge } from "@/components/badges/Badge";
import { Button } from "@/components/buttons/Button";
import { extractErrorMessage } from "@/utils/apiError";
import {
  orchestratorApi,
  type OrchestratorStatus,
  type OrchestratorTask,
  type OrchestratorTasks,
  type OrchestratorHealth,
  type OrchestratorAnalytics,
  type OrchestratorAuditEntry,
  type OrchestratorMemory,
  type OrchestratorIntegrations,
} from "@/api/orchestrator";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const statusVariant = (status?: string): "success" | "warning" | "danger" | "default" => {
  const s = status?.toLowerCase() ?? "";
  if (s === "completed" || s === "healthy" || s === "ok") return "success";
  if (s === "running" || s === "queued" || s === "waiting_approval") return "warning";
  if (s === "failed" || s === "cancelled" || s === "rejected") return "danger";
  return "default";
};

const taskStatusBadge = (status?: string) => {
  const v = statusVariant(status);
  const labels: Record<string, string> = {
    pending: "Pendente",
    queued: "Na fila",
    waiting_approval: "Aguardando aprovação",
    scheduled: "Agendado",
    running: "Executando",
    completed: "Concluído",
    failed: "Falhou",
    cancelled: "Cancelado",
    paused: "Pausado",
    rolled_back: "Rollback",
  };
  return <Badge variant={v} size="sm">{labels[status ?? ""] ?? status ?? "—"}</Badge>;
};

const fmtTimestamp = (ts?: number): string =>
  ts ? new Date(ts * 1000).toLocaleString("pt-BR") : "—";

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function SuperAiOrchestratorPage() {
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  // Section payloads
  const [status, setStatus] = useState<OrchestratorStatus | null>(null);
  const [health, setHealth] = useState<OrchestratorHealth | null>(null);
  const [tasks, setTasks] = useState<OrchestratorTask[] | null>(null);
  const [governance, setGovernance] = useState<Record<string, unknown> | null>(null);
  const [analytics, setAnalytics] = useState<OrchestratorAnalytics | null>(null);
  const [audit, setAudit] = useState<OrchestratorAuditEntry[] | null>(null);
  const [memory, setMemory] = useState<OrchestratorMemory | null>(null);
  const [integrations, setIntegrations] = useState<OrchestratorIntegrations | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const [statusData, healthData, tasksData, govData, analyticsData, auditData, memoryData, integrationsData] =
        await Promise.all([
          orchestratorApi.status(),
          orchestratorApi.health(),
          orchestratorApi.tasks(),
          orchestratorApi.governance(),
          orchestratorApi.analytics(),
          orchestratorApi.audit(),
          orchestratorApi.memoryNamespaces(),
          orchestratorApi.integrations(),
        ]);
      setStatus(statusData);
      setHealth(healthData);
      setTasks((tasksData.tasks ?? []) as OrchestratorTask[]);
      setGovernance(govData);
      setAnalytics(analyticsData);
      setAudit(auditData);
      setMemory(memoryData);
      setIntegrations(integrationsData);
    } catch (e) {
      setLoadError(extractErrorMessage(e, "Falha ao carregar o orquestrador"));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const handleApprove = async (seq: number) => {
    try {
      await orchestratorApi.approve(seq);
      await refresh();
    } catch (e) {
      setLoadError(extractErrorMessage(e, "Falha ao aprovar tarefa"));
    }
  };

  const handleCancel = async (seq: number) => {
    try {
      await orchestratorApi.cancel(seq);
      await refresh();
    } catch (e) {
      setLoadError(extractErrorMessage(e, "Falha ao cancelar tarefa"));
    }
  };

  const handlePause = async (seq: number) => {
    try {
      await orchestratorApi.pause(seq);
      await refresh();
    } catch (e) {
      setLoadError(extractErrorMessage(e, "Falha ao pausar tarefa"));
    }
  };

  const handleResume = async (seq: number) => {
    try {
      await orchestratorApi.resume(seq);
      await refresh();
    } catch (e) {
      setLoadError(extractErrorMessage(e, "Falha ao retomar tarefa"));
    }
  };

  const handleRollback = async (seq: number) => {
    try {
      await orchestratorApi.rollback(seq);
      await refresh();
    } catch (e) {
      setLoadError(extractErrorMessage(e, "Falha ao reverter tarefa"));
    }
  };

  const handleTick = async () => {
    try {
      await orchestratorApi.tick(20);
      await refresh();
    } catch (e) {
      setLoadError(extractErrorMessage(e, "Falha ao executar tick"));
    }
  };

  // Derived values
  const kernel = status?.kernel ?? {};
  const running = typeof kernel.running === "number" ? kernel.running : 0;
  const queued = typeof kernel.queued === "number" ? kernel.queued : 0;
  const completed = typeof kernel.completed === "number" ? kernel.completed : 0;
  const failed = typeof kernel.failed === "number" ? kernel.failed : 0;
  const cancelled = typeof kernel.cancelled === "number" ? kernel.cancelled : 0;
  const paused = typeof kernel.paused === "number" ? kernel.paused : 0;
  const waitingApproval = typeof kernel.waiting_approval === "number" ? kernel.waiting_approval : 0;

  const auditEntries = (audit ?? []).slice(0, 15);
  const memoryNamespaces = memory?.namespaces ?? [];
  const integrationEntries = integrations ? Object.entries(integrations) : [];

  return (
    <DashboardLayout>
      {/* ─── Header ─────────────────────────────────────────────────── */}
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 text-2xl shadow-lg">
            ⚙️
          </div>
          <div>
            <h1 className="text-2xl font-bold text-surface-900 dark:text-surface-50">
              Super AI Orchestrator
            </h1>
            <p className="mt-0.5 text-sm text-surface-500">
              Painel de controle do pipeline multi-agente
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant={health?.status === "healthy" ? "success" : "warning"} size="md" dot>
            {loading ? "Carregando…" : health?.status ?? "—"}
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

      {/* ─── Status & Kernel Metrics ───────────────────────────────── */}
      <div className="mb-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader>
            <h2 className="text-sm font-semibold text-surface-900 dark:text-surface-50">
              Executando
            </h2>
          </CardHeader>
          <CardBody>
            <p className="text-3xl font-bold text-surface-900 dark:text-surface-50">{running}</p>
          </CardBody>
        </Card>
        <Card>
          <CardHeader>
            <h2 className="text-sm font-semibold text-surface-900 dark:text-surface-50">
              Na fila
            </h2>
          </CardHeader>
          <CardBody>
            <p className="text-3xl font-bold text-surface-900 dark:text-surface-50">{queued}</p>
          </CardBody>
        </Card>
        <Card>
          <CardHeader>
            <h2 className="text-sm font-semibold text-surface-900 dark:text-surface-50">
              Concluídos
            </h2>
          </CardHeader>
          <CardBody>
            <p className="text-3xl font-bold text-success-600 dark:text-success-400">{completed}</p>
          </CardBody>
        </Card>
        <Card>
          <CardHeader>
            <h2 className="text-sm font-semibold text-surface-900 dark:text-surface-50">
              Falhas
            </h2>
          </CardHeader>
          <CardBody>
            <p className="text-3xl font-bold text-danger-600 dark:text-danger-400">{failed}</p>
          </CardBody>
        </Card>
      </div>

      {/* ─── Governance & Config ───────────────────────────────────── */}
      <div className="mb-8 grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
              Governança
            </h2>
            <Badge variant="info" size="sm">Política</Badge>
          </CardHeader>
          <CardBody>
            {governance === null ? (
              <p className="py-4 text-center text-sm text-surface-400">Carregando…</p>
            ) : (
              <pre className="whitespace-pre-wrap text-sm text-surface-700 dark:text-surface-300">
                {JSON.stringify(governance, null, 2)}
              </pre>
            )}
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
              Configuração
            </h2>
            <Badge variant="default" size="sm">Kernel</Badge>
          </CardHeader>
          <CardBody>
            {status === null ? (
              <p className="py-4 text-center text-sm text-surface-400">Carregando…</p>
            ) : (
              <pre className="whitespace-pre-wrap text-sm text-surface-700 dark:text-surface-300">
                {JSON.stringify(status, null, 2)}
              </pre>
            )}
          </CardBody>
        </Card>
      </div>

      {/* ─── Tasks ──────────────────────────────────────────────────── */}
      <Card className="mb-8">
        <CardHeader>
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
              Tarefas Recentes
            </h2>
            <div className="flex gap-2">
              <Button variant="primary" size="sm" onClick={handleTick}>
              ▶ Tick (20 fatias)
              </Button>
            </div>
          </div>
          <Badge variant="default" size="sm">{tasks?.length ?? 0} tarefas</Badge>
        </CardHeader>
        <CardBody>
          {!tasks || tasks.length === 0 ? (
            <p className="py-4 text-center text-sm text-surface-400">
              Nenhuma tarefa no momento.
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-surface-200 text-xs uppercase tracking-wide text-surface-400 dark:border-surface-700">
                    <th className="pb-2 pr-4 font-medium">Seq</th>
                    <th className="pb-2 pr-4 font-medium">Tipo</th>
                    <th className="pb-2 pr-4 font-medium">Título</th>
                    <th className="pb-2 pr-4 font-medium">Status</th>
                    <th className="pb-2 pr-4 font-medium">Prioridade</th>
                    <th className="pb-2 pr-4 font-medium">Dono</th>
                    <th className="pb-2 font-medium">Ações</th>
                  </tr>
                </thead>
                <tbody>
                  {tasks.slice(0, 20).map((task) => (
                    <tr
                      key={task.seq}
                      className="border-b border-surface-100 last:border-0 dark:border-surface-800"
                    >
                      <td className="py-2.5 pr-4 tabular-nums text-surface-900 dark:text-surface-50">
                        {task.seq}
                      </td>
                      <td className="py-2.5 pr-4 text-surface-700 dark:text-surface-300">
                        {task.kind ?? "—"}
                      </td>
                      <td className="py-2.5 pr-4 text-surface-900 dark:text-surface-50">
                        {task.title ?? "—"}
                      </td>
                      <td className="py-2.5 pr-4">{taskStatusBadge(task.status)}</td>
                      <td className="py-2.5 pr-4 text-surface-700 dark:text-surface-300">
                        {task.priority ?? "—"}
                      </td>
                      <td className="py-2.5 pr-4 text-surface-700 dark:text-surface-300">
                        {task.owner ?? "—"}
                      </td>
                      <td className="py-2.5 text-surface-700 dark:text-surface-300">
                        <div className="flex gap-1">
                          {task.status === "waiting_approval" && (
                            <>
                              <Button
                                variant="primary"
                                size="xs"
                                onClick={() => handleApprove(task.seq!)}
                              >
                                Aprovar
                              </Button>
                              <Button
                                variant="danger"
                                size="xs"
                                onClick={() => handleCancel(task.seq!)}
                              >
                                Rejeitar
                              </Button>
                            </>
                          )}
                          {task.status === "paused" && (
                            <Button variant="secondary" size="xs" onClick={() => handleResume(task.seq!)}>
                              Retomar
                            </Button>
                          )}
                          {task.status === "running" && (
                            <>
                              <Button variant="warning" size="xs" onClick={() => handlePause(task.seq!)}>
                                Pausar
                              </Button>
                              <Button variant="danger" size="xs" onClick={() => handleCancel(task.seq!)}>
                                Cancelar
                              </Button>
                            </>
                          )}
                          {task.status === "failed" && (
                            <Button variant="secondary" size="xs" onClick={() => handleRollback(task.seq!)}>
                              Rollback
                            </Button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardBody>
      </Card>

      {/* ─── Analytics & Audit ─────────────────────────────────────── */}
      <div className="mb-8 grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
              Analytics
            </h2>
            <Badge variant="primary" size="sm">Métricas</Badge>
          </CardHeader>
          <CardBody>
            {analytics === null ? (
              <p className="py-4 text-center text-sm text-surface-400">Carregando…</p>
            ) : (
              <pre className="whitespace-pre-wrap text-sm text-surface-700 dark:text-surface-300">
                {JSON.stringify(analytics, null, 2)}
              </pre>
            )}
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
              Auditoria
            </h2>
            <Badge variant="default" size="sm">{auditEntries.length} entradas</Badge>
          </CardHeader>
          <CardBody>
            {!auditEntries.length ? (
              <p className="py-4 text-center text-sm text-surface-400">
                Nenhuma entrada de auditoria.
              </p>
            ) : (
              <div className="space-y-2">
                {auditEntries.map((entry, i) => (
                  <div
                    key={i}
                    className="rounded-lg border border-surface-100 p-3 dark:border-surface-800"
                  >
                    <div className="flex items-center gap-2">
                      <Badge variant={statusVariant(entry.status as string)} size="sm">
                        {entry.status ?? "—"}
                      </Badge>
                      <span className="text-xs text-surface-400">
                        {fmtTimestamp(entry.timestamp as number)}
                      </span>
                    </div>
                    <p className="mt-1 text-sm text-surface-700 dark:text-surface-300">
                      {entry.action ?? "—"}
                    </p>
                    {entry.detail && (
                      <p className="mt-0.5 text-xs text-surface-400">
                        {String(entry.detail)}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </CardBody>
        </Card>
      </div>

      {/* ─── Memory & Integrations ─────────────────────────────────── */}
      <div className="mb-8 grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
              Memória
            </h2>
            <Badge variant="default" size="sm">{memoryNamespaces.length} namespaces</Badge>
          </CardHeader>
          <CardBody>
            {!memoryNamespaces.length ? (
              <p className="py-4 text-center text-sm text-surface-400">
                Nenhum namespace de memória.
              </p>
            ) : (
              <div className="flex flex-wrap gap-2">
                {memoryNamespaces.map((ns) => (
                  <Badge key={ns} variant="info" size="sm">
                    {ns}
                  </Badge>
                ))}
              </div>
            )}
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
              Integrações
            </h2>
            <Badge variant="default" size="sm">{integrationEntries.length} conectores</Badge>
          </CardHeader>
          <CardBody>
            {!integrationEntries.length ? (
              <p className="py-4 text-center text-sm text-surface-400">
                Nenhuma integração configurada.
              </p>
            ) : (
              <div className="space-y-2">
                {integrationEntries.map(([name, info]) => (
                  <div
                    key={name}
                    className="flex items-center justify-between rounded-lg border border-surface-100 p-3 dark:border-surface-800"
                  >
                    <span className="text-sm font-medium text-surface-900 dark:text-surface-50">
                      {name}
                    </span>
                    <Badge variant="success" size="sm">ativo</Badge>
                  </div>
                ))}
              </div>
            )}
          </CardBody>
        </Card>
      </div>

      {/* ─── Back link ─────────────────────────────────────────────── */}
      <div className="mt-6">
        <Link href="/dashboard" className="text-sm text-primary-600 hover:text-primary-700 dark:text-primary-400">
          ← Voltar ao Dashboard
        </Link>
      </div>
    </DashboardLayout>
  );
}
