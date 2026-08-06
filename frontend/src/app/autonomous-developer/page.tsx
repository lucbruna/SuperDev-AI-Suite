"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { DashboardLayout } from "@/components/DashboardLayout";
import { Card, CardHeader, CardBody } from "@/components/cards/Card";
import { Badge } from "@/components/badges/Badge";
import { Button } from "@/components/buttons/Button";
import { extractErrorMessage } from "@/utils/apiError";
import {
  autonomousDeveloperApi,
  type DeveloperStatus,
  type DeveloperSession,
} from "@/api/autonomousDeveloper";

export default function AutonomousDeveloperPage() {
  const [status, setStatus] = useState<DeveloperStatus | null>(null);
  const [sessions, setSessions] = useState<DeveloperSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [goal, setGoal] = useState("");
  const [executeLoading, setExecuteLoading] = useState(false);
  const [executeError, setExecuteError] = useState<string | null>(null);
  const [executeResult, setExecuteResult] = useState<Record<string, unknown> | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const [statusData, sessionsData] = await Promise.all([
        autonomousDeveloperApi.status(),
        autonomousDeveloperApi.sessions(10),
      ]);
      setStatus(statusData);
      setSessions([...(sessionsData.active ?? []), ...(sessionsData.recent ?? [])]);
    } catch (e) {
      setLoadError(extractErrorMessage(e, "Falha ao carregar o Autonomous Developer"));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const execute = async () => {
    if (!goal.trim()) return;
    setExecuteLoading(true);
    setExecuteError(null);
    setExecuteResult(null);
    try {
      const data = await autonomousDeveloperApi.execute({ goal: goal.trim() });
      setExecuteResult(data as Record<string, unknown>);
      await refresh();
    } catch (e) {
      setExecuteError(extractErrorMessage(e, "Falha ao executar a missão"));
    } finally {
      setExecuteLoading(false);
    }
  };

  const reset = async () => {
    setExecuteLoading(true);
    setExecuteError(null);
    setExecuteResult(null);
    try {
      const data = await autonomousDeveloperApi.reset();
      setExecuteResult(data as Record<string, unknown>);
      await refresh();
    } catch (e) {
      setExecuteError(extractErrorMessage(e, "Falha ao resetar o agente"));
    } finally {
      setExecuteLoading(false);
    }
  };

  return (
    <DashboardLayout>
      {/* ─── Header ──────────────────────────────────────────────────── */}
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500 to-purple-700 text-2xl shadow-lg">
            🤖
          </div>
          <div>
            <h1 className="text-2xl font-bold text-surface-900 dark:text-surface-50">
              Autonomous Developer
            </h1>
            <p className="mt-0.5 text-sm text-surface-500">
              Agente autônomo de desenvolvimento de código
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant={loading ? "default" : !loadError ? "success" : "danger"} size="md" dot>
            {loading ? "Carregando…" : !loadError ? "Operacional" : "Offline"}
          </Badge>
          <Button variant="secondary" size="sm" onClick={refresh}>
            ⟳ Recarregar
          </Button>
        </div>
      </div>

      {loadError && (
        <div className="mb-6 rounded-lg bg-red-50 px-3 py-2.5 text-sm text-red-600 dark:bg-red-950/40 dark:text-red-400">
          {loadError}
        </div>
      )}

      {/* ─── Status ───────────────────────────────────────────────────── */}
      <div className="mb-8 grid grid-cols-2 gap-3 sm:grid-cols-4">
        {[
          { label: "Modo", value: status?.config?.mode ?? "—", icon: "⚙️" },
          { label: "Sessões ativas", value: status?.sessions_active ?? "—", icon: "💼" },
          { label: "Branch", value: status?.config?.work_branch ?? "—", icon: "🌿" },
          { label: "Artefatos", value: status?.artifacts?.length ?? "—", icon: "📦" },
        ].map((tile) => (
          <div
            key={tile.label}
            className="flex items-center gap-3 rounded-xl border border-surface-200 bg-white p-4 dark:border-surface-700 dark:bg-surface-900"
          >
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-surface-100 text-lg dark:bg-surface-800">
              {tile.icon}
            </div>
            <div className="min-w-0">
              <p className="text-xl font-bold tabular-nums text-surface-900 dark:text-surface-50">
                {tile.value}
              </p>
              <p className="text-xs text-surface-500">{tile.label}</p>
            </div>
          </div>
        ))}
      </div>

      {/* ─── Execute ─────────────────────────────────────────────────── */}
      <Card className="mb-8">
        <CardHeader>
          <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
            Nova missão
          </h2>
          <Badge variant="default" size="sm">Executar</Badge>
        </CardHeader>
        <CardBody>
          <textarea
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
            placeholder="Descreva a tarefa que o agente deve executar…"
            rows={3}
            className="w-full resize-y rounded-lg border border-surface-300 bg-white px-3 py-2 text-sm text-surface-900 outline-none focus:border-primary-500 dark:border-surface-600 dark:bg-surface-800 dark:text-surface-100"
          />
          <div className="mt-3 flex flex-wrap gap-2">
            <Button
              variant="primary"
              size="sm"
              onClick={() => void execute()}
              isLoading={executeLoading}
              disabled={!goal.trim()}
            >
              🚀 Executar
            </Button>
            <Button variant="secondary" size="sm" onClick={() => void reset()} isLoading={executeLoading}>
              ⟲ Resetar
            </Button>
          </div>
          {executeError && <p className="mt-3 text-xs text-red-500">{executeError}</p>}
          {executeResult && (
            <pre className="mt-3 max-h-72 overflow-auto rounded-lg bg-surface-100 p-3 text-xs leading-relaxed text-surface-700 dark:bg-surface-800 dark:text-surface-300">
              {JSON.stringify(executeResult, null, 2)}
            </pre>
          )}
        </CardBody>
      </Card>

      {/* ─── Sessions ────────────────────────────────────────────────── */}
      <Card className="mb-8">
        <CardHeader>
          <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
            Sessões
          </h2>
          <Badge variant="primary" size="sm">{sessions.length} sessões</Badge>
        </CardHeader>
        <CardBody>
          {sessions.length === 0 ? (
            <p className="text-sm text-surface-400">Nenhuma sessão registrada.</p>
          ) : (
            <ul className="divide-y divide-surface-200 dark:divide-surface-700">
              {sessions.map((s, i) => (
                <li key={s.session_id ?? i} className="flex items-start justify-between gap-4 py-2.5">
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-surface-900 dark:text-surface-50">
                      {s.goal ?? s.session_id ?? "sessão"}
                    </p>
                    <p className="text-xs text-surface-500">{s.project_root}</p>
                  </div>
                  <div className="flex shrink-0 items-center gap-2">
                    <Badge
                      variant={s.status === "active" ? "success" : "default"}
                      size="sm"
                    >
                      {s.status ?? "—"}
                    </Badge>
                    <span className="text-xs tabular-nums text-surface-400">
                      {s.elapsed_seconds != null ? `${s.elapsed_seconds}s` : "—"}
                    </span>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </CardBody>
      </Card>

      <div className="mt-6">
        <Link href="/dashboard" className="text-sm text-primary-600 hover:text-primary-700 dark:text-primary-400">
          ← Voltar ao Dashboard
        </Link>
      </div>
    </DashboardLayout>
  );
}