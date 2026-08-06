"use client";

import { useCallback, useEffect, useState } from "react";
import { orchestratorApi, type OrchestratorTask } from "@/api/orchestrator";
import { Badge } from "@/components/badges/Badge";
import { Button } from "@/components/buttons/Button";
import { ActionFeedback, ControlSection, errMsg, unwrapList, unwrapObj } from "./ControlSection";

const taskVariant: Record<string, "default" | "primary" | "success" | "warning" | "danger" | "info"> = {
  completed: "success",
  running: "info",
  approved: "success",
  pending: "warning",
  paused: "warning",
  cancelled: "default",
  failed: "danger",
  rejected: "danger",
  waiting: "warning",
};

export function OrchestratorPanel() {
  const [status, setStatus] = useState<Record<string, unknown>>({});
  const [tasks, setTasks] = useState<OrchestratorTask[]>([]);
  const [analytics, setAnalytics] = useState<Record<string, unknown>>({});
  const [loading, setLoading] = useState(false);
  const [busy, setBusy] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [showNew, setShowNew] = useState(false);
  const [newKind, setNewKind] = useState("analysis");
  const [newTitle, setNewTitle] = useState("");

  const load = useCallback(async (showSpinner = true) => {
    if (showSpinner) setLoading(true);
    try {
      const [s, t, a] = await Promise.all([
        orchestratorApi.status(),
        orchestratorApi.tasks(),
        orchestratorApi.analytics(),
      ]);
      setStatus(unwrapObj(s));
      setTasks(unwrapList<OrchestratorTask>(t));
      setAnalytics(unwrapObj(a));
    } catch (e) {
      setFeedback(`❌ ${errMsg(e)}`);
    } finally {
      if (showSpinner) setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const run = async (action: string, fn: () => Promise<unknown>, msg: string) => {
    setBusy(action);
    setFeedback(null);
    try {
      await fn();
      setFeedback(`✅ ${msg}`);
      await load(false);
    } catch (e) {
      setFeedback(`❌ ${errMsg(e)}`);
    } finally {
      setBusy(null);
    }
  };

  const running = status.running as boolean | undefined;
  const taskCount = (analytics.total_tasks as number) ?? tasks.length;
  const pendingCount = (analytics.pending as number) ?? tasks.filter((t) => t.status === "pending").length;

  return (
    <ControlSection
      icon="🎯"
      title="Orquestrador Multi-Agente"
      subtitle="Tarefas, aprovações e ciclo de processamento"
      action={
        <Button variant="secondary" size="sm" onClick={() => load()} disabled={loading}>
          {loading ? "..." : "⟳"}
        </Button>
      }
    >
      <div className="flex flex-wrap items-center gap-2 mb-4">
        <Badge variant={running ? "success" : "warning"} dot>
          {running ? "Rodando" : "Parado"}
        </Badge>
        <Badge variant="info">{taskCount} tarefas</Badge>
        {pendingCount > 0 && <Badge variant="warning">{pendingCount} aguardando aprovação</Badge>}
        <div className="ml-auto flex gap-2">
          <Button
            variant="primary"
            size="sm"
            isLoading={busy === "tick"}
            onClick={() =>
              run("tick", () => orchestratorApi.tick(1), `Tick processado (${new Date().toLocaleTimeString("pt-BR")})`)
            }
          >
            ▶ Tick
          </Button>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => setShowNew((v) => !v)}
          >
            ➕ Nova Tarefa
          </Button>
        </div>
      </div>

      {showNew && (
        <div className="mb-4 rounded-lg border border-surface-200 bg-surface-50 p-3 space-y-2 dark:border-surface-700 dark:bg-surface-800">
          <div className="flex gap-2">
            <select
              value={newKind}
              onChange={(e) => setNewKind(e.target.value)}
              className="rounded-lg border border-surface-300 bg-white px-2 py-1.5 text-sm text-surface-900 dark:border-surface-600 dark:bg-surface-900 dark:text-surface-100"
            >
              {["analysis", "coding", "review", "research", "automation", "ops"].map((k) => (
                <option key={k} value={k}>{k}</option>
              ))}
            </select>
            <input
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              placeholder="Descreva a tarefa..."
              className="min-w-0 flex-1 rounded-lg border border-surface-300 bg-white px-3 py-1.5 text-sm text-surface-900 dark:border-surface-600 dark:bg-surface-900 dark:text-surface-100"
            />
            <Button
              variant="primary"
              size="sm"
              isLoading={busy === "new"}
              disabled={!newTitle.trim()}
              onClick={() =>
                run(
                  "new",
                  () => orchestratorApi.submitTask({ kind: newKind, title: newTitle.trim() }),
                  `Tarefa criada: ${newTitle.trim()}`,
                ).then(() => {
                  setNewTitle("");
                  setShowNew(false);
                })
              }
            >
              Criar
            </Button>
          </div>
        </div>
      )}

      {tasks.length === 0 ? (
        <p className="text-center text-sm text-surface-400 py-6">
          Nenhuma tarefa no orquestrador
        </p>
      ) : (
        <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
          {tasks.slice(0, 15).map((t) => {
            const seq = t.seq as number;
            const st = (t.status as string) ?? "unknown";
            return (
              <div
                key={seq}
                className="flex flex-wrap items-center gap-2 rounded-lg border border-surface-100 bg-surface-50/50 px-3 py-2 dark:border-surface-800 dark:bg-surface-800/50"
              >
                <span className="text-xs font-mono text-surface-400">#{seq}</span>
                <Badge variant="default" size="sm">{t.kind}</Badge>
                <span className="min-w-0 flex-1 truncate text-sm text-surface-900 dark:text-surface-50">
                  {t.title}
                </span>
                <Badge variant={taskVariant[st] ?? "default"} size="sm">{st}</Badge>
                {st === "pending" && (
                  <>
                    <Button variant="primary" size="sm" isLoading={busy === `ap${seq}`}
                      onClick={() => run(`ap${seq}`, () => orchestratorApi.approve(seq), `Tarefa #${seq} aprovada`)}>
                      ✓
                    </Button>
                    <Button variant="danger" size="sm" isLoading={busy === `rj${seq}`}
                      onClick={() => run(`rj${seq}`, () => orchestratorApi.reject(seq), `Tarefa #${seq} rejeitada`)}>
                      ✕
                    </Button>
                  </>
                )}
                {(st === "running" || st === "pending") && (
                  <Button variant="secondary" size="sm" isLoading={busy === `cx${seq}`}
                    onClick={() => run(`cx${seq}`, () => orchestratorApi.cancel(seq), `Tarefa #${seq} cancelada`)}>
                    ⏹
                  </Button>
                )}
                {st === "running" && (
                  <Button variant="secondary" size="sm" isLoading={busy === `ps${seq}`}
                    onClick={() => run(`ps${seq}`, () => orchestratorApi.pause(seq), `Tarefa #${seq} pausada`)}>
                    ⏸
                  </Button>
                )}
                {st === "paused" && (
                  <Button variant="secondary" size="sm" isLoading={busy === `rs${seq}`}
                    onClick={() => run(`rs${seq}`, () => orchestratorApi.resume(seq), `Tarefa #${seq} retomada`)}>
                    ▶
                  </Button>
                )}
              </div>
            );
          })}
        </div>
      )}

      <ActionFeedback message={feedback} />
    </ControlSection>
  );
}
