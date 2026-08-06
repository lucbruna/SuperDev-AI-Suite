"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { DashboardLayout } from "@/components/DashboardLayout";
import { Card, CardHeader, CardBody } from "@/components/cards/Card";
import { Badge } from "@/components/badges/Badge";
import { Button } from "@/components/buttons/Button";
import { extractErrorMessage } from "@/utils/apiError";
import {
  selfHealingApi,
  type HealingStatus,
  type HealingEvent,
} from "@/api/selfHealing";

export default function SelfHealingPage() {
  const [status, setStatus] = useState<HealingStatus | null>(null);
  const [events, setEvents] = useState<HealingEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [runLoading, setRunLoading] = useState(false);
  const [runError, setRunError] = useState<string | null>(null);
  const [runResult, setRunResult] = useState<Record<string, unknown> | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const [statusData, eventsData] = await Promise.all([
        selfHealingApi.status(),
        selfHealingApi.events(),
      ]);
      setStatus(statusData);
      setEvents(eventsData.events ?? []);
    } catch (e) {
      setLoadError(extractErrorMessage(e, "Falha ao carregar o Self-Healing"));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const runHealing = async () => {
    setRunLoading(true);
    setRunError(null);
    setRunResult(null);
    try {
      const data = await selfHealingApi.run();
      setRunResult(data as Record<string, unknown>);
      await refresh();
    } catch (e) {
      setRunError(extractErrorMessage(e, "Falha ao executar o ciclo de cura"));
    } finally {
      setRunLoading(false);
    }
  };

  const healthy = !loadError;

  return (
    <DashboardLayout>
      {/* ─── Header ──────────────────────────────────────────────────── */}
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-rose-500 to-red-700 text-2xl shadow-lg">
            🩺
          </div>
          <div>
            <h1 className="text-2xl font-bold text-surface-900 dark:text-surface-50">
              Self-Healing Engine
            </h1>
            <p className="mt-0.5 text-sm text-surface-500">
              Detecção e recuperação automática de falhas
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant={loading ? "default" : healthy ? "success" : "danger"} size="md" dot>
            {loading ? "Carregando…" : healthy ? "Operacional" : "Offline"}
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
          { label: "Ciclos", value: status?.cycles ?? "—", icon: "🔁" },
          { label: "Eventos", value: status?.events ?? "—", icon: "📡" },
          { label: "Memória", value: status?.memory ?? "—", icon: "🧠" },
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

      {/* ─── Run healing ─────────────────────────────────────────────── */}
      <Card className="mb-8">
        <CardHeader>
          <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
            Executar ciclo de cura
          </h2>
          <Badge variant="default" size="sm">Manual</Badge>
        </CardHeader>
        <CardBody>
          <div className="flex flex-wrap items-center gap-2">
            <Button variant="primary" size="sm" onClick={() => void runHealing()} isLoading={runLoading}>
              🩺 Executar ciclo
            </Button>
          </div>
          {runError && <p className="mt-3 text-xs text-red-500">{runError}</p>}
          {runResult && (
            <pre className="mt-3 max-h-72 overflow-auto rounded-lg bg-surface-100 p-3 text-xs leading-relaxed text-surface-700 dark:bg-surface-800 dark:text-surface-300">
              {JSON.stringify(runResult, null, 2)}
            </pre>
          )}
        </CardBody>
      </Card>

      {/* ─── Events ──────────────────────────────────────────────────── */}
      <Card className="mb-8">
        <CardHeader>
          <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
            Eventos recentes
          </h2>
          <Badge variant="primary" size="sm">{events.length} eventos</Badge>
        </CardHeader>
        <CardBody>
          {events.length === 0 ? (
            <p className="text-sm text-surface-400">Nenhum evento registrado.</p>
          ) : (
            <ul className="divide-y divide-surface-200 dark:divide-surface-700">
              {events.map((ev, i) => (
                <li key={i} className="flex items-start justify-between gap-4 py-2.5">
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-surface-900 dark:text-surface-50">
                      {ev.event_type ?? "evento"}
                    </p>
                    {ev.payload && (
                      <pre className="mt-1 max-h-32 overflow-auto rounded bg-surface-100 p-2 text-[11px] leading-relaxed text-surface-600 dark:bg-surface-800 dark:text-surface-300">
                        {JSON.stringify(ev.payload, null, 2)}
                      </pre>
                    )}
                  </div>
                  <span className="shrink-0 text-xs tabular-nums text-surface-400">
                    #{ev.sequence ?? "—"}
                  </span>
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