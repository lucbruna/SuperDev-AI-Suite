"use client";

import { useCallback, useEffect, useState } from "react";
import { systemApi } from "@/api/system";
import { Badge } from "@/components/badges/Badge";
import { Button } from "@/components/buttons/Button";
import { ActionFeedback, ControlSection, errMsg, unwrapList, unwrapObj } from "./ControlSection";

export function SystemPanel() {
  const [status, setStatus] = useState<Record<string, unknown>>({});
  const [agents, setAgents] = useState<Record<string, unknown>[]>([]);
  const [scheduler, setScheduler] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(false);
  const [busy, setBusy] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);

  const load = useCallback(async (showSpinner = true) => {
    if (showSpinner) setLoading(true);
    try {
      const [s, a, sch] = await Promise.all([
        systemApi.status(),
        systemApi.agents(),
        systemApi.schedulerTasks(),
      ]);
      setStatus(unwrapObj(s));
      setAgents(unwrapList<Record<string, unknown>>(a));
      setScheduler(unwrapList<Record<string, unknown>>(sch));
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

  const st = status.status as string | undefined;

  return (
    <ControlSection
      icon="🖥️"
      title="Sistema"
      subtitle="Status, diagnóstico e agendador do backend"
      action={
        <Button variant="secondary" size="sm" onClick={() => load()} disabled={loading}>
          {loading ? "..." : "⟳"}
        </Button>
      }
    >
      <div className="flex flex-wrap items-center gap-2 mb-4">
        <Badge variant={st === "running" || st === "ok" ? "success" : "default"} dot>
          {st ?? "desconhecido"}
        </Badge>
        {status.version ? <Badge variant="info">v{String(status.version)}</Badge> : null}
        {status.uptime_seconds ? (
          <Badge variant="default">uptime {String(status.uptime_seconds)}s</Badge>
        ) : null}
        <div className="ml-auto flex flex-wrap gap-2">
          <Button
            variant="secondary"
            size="sm"
            isLoading={busy === "selftest"}
            onClick={() => run("selftest", () => systemApi.selfTest(), "Self-test concluído")}
          >
            🧪 Self-Test
          </Button>
          <Button
            variant="primary"
            size="sm"
            isLoading={busy === "boot"}
            onClick={() => run("boot", () => systemApi.boot(), "Boot iniciado")}
          >
            🚀 Boot
          </Button>
          <Button
            variant="danger"
            size="sm"
            isLoading={busy === "shutdown"}
            onClick={() => {
              if (window.confirm("Confirmar desligamento do sistema?")) {
                run("shutdown", () => systemApi.shutdown(), "Sistema desligado");
              }
            }}
          >
            🛑 Shutdown
          </Button>
        </div>
      </div>

      {agents.length > 0 && (
        <div className="mb-4">
          <p className="mb-2 text-xs font-medium text-surface-400 uppercase tracking-wider">
            Agentes do sistema
          </p>
          <div className="space-y-2">
            {agents.slice(0, 6).map((a) => {
              const id = String(a.id ?? a.name ?? "");
              const agentStatus = String(a.status ?? "unknown");
              return (
                <div key={id} className="flex items-center gap-2 rounded-lg border border-surface-100 bg-surface-50/50 px-3 py-2 dark:border-surface-800 dark:bg-surface-800/50">
                  <span className="min-w-0 flex-1 truncate text-sm text-surface-900 dark:text-surface-50">
                    {String(a.name ?? id)}
                  </span>
                  <Badge
                    variant={agentStatus === "running" ? "success" : agentStatus === "stopped" ? "default" : "warning"}
                    size="sm"
                  >
                    {agentStatus}
                  </Badge>
                  {agentStatus === "running" ? (
                    <Button variant="secondary" size="sm" isLoading={busy === `stop-${id}`}
                      onClick={() => run(`stop-${id}`, () => systemApi.stopAgent(id), `Agente ${a.name ?? id} parado`)}>
                      ⏹
                    </Button>
                  ) : (
                    <Button variant="primary" size="sm" isLoading={busy === `start-${id}`}
                      onClick={() => run(`start-${id}`, () => systemApi.startAgent(id), `Agente ${a.name ?? id} iniciado`)}>
                      ▶
                    </Button>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {scheduler.length > 0 && (
        <div>
          <p className="mb-2 text-xs font-medium text-surface-400 uppercase tracking-wider">
            Tarefas agendadas
          </p>
          <div className="space-y-2">
            {scheduler.slice(0, 6).map((t) => {
              const id = String(t.id ?? t.name ?? "");
              return (
                <div key={id} className="flex items-center gap-2 rounded-lg border border-surface-100 bg-surface-50/50 px-3 py-2 dark:border-surface-800 dark:bg-surface-800/50">
                  <span className="min-w-0 flex-1 truncate text-sm text-surface-900 dark:text-surface-50">
                    {String(t.name ?? id)}
                  </span>
                  {t.cron ? (
                    <span className="font-mono text-xs text-surface-400">{String(t.cron)}</span>
                  ) : null}
                  <Badge variant={t.enabled ? "success" : "default"} size="sm">
                    {t.enabled ? "ativo" : "inativo"}
                  </Badge>
                  <Button variant="secondary" size="sm" isLoading={busy === `run-${id}`}
                    onClick={() => run(`run-${id}`, () => systemApi.runSchedulerTask(id), `Tarefa ${t.name ?? id} executada`)}>
                    ▶ Executar
                  </Button>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {agents.length === 0 && scheduler.length === 0 && (
        <p className="text-center text-sm text-surface-400 py-4">
          Sem agentes ou tarefas agendadas
        </p>
      )}

      <ActionFeedback message={feedback} />
    </ControlSection>
  );
}
