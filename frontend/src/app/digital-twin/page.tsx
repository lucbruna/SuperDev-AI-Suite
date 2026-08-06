"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { DashboardLayout } from "@/components/DashboardLayout";
import { Card, CardHeader, CardBody } from "@/components/cards/Card";
import { Badge } from "@/components/badges/Badge";
import { Button } from "@/components/buttons/Button";
import { extractErrorMessage } from "@/utils/apiError";
import {
  digitalTwinApi,
  type DigitalTwinState,
  type DigitalTwinConfig,
} from "@/api/digitalTwin";

export default function DigitalTwinPage() {
  const [state, setState] = useState<DigitalTwinState | null>(null);
  const [config, setConfig] = useState<DigitalTwinConfig | null>(null);
  const [endpoints, setEndpoints] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [actionLoading, setActionLoading] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);

  const [twinName, setTwinName] = useState("default");
  const [steps, setSteps] = useState(1);

  const refresh = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const [stateData, configData, endpointsData] = await Promise.all([
        digitalTwinApi.status(),
        digitalTwinApi.config(),
        digitalTwinApi.endpoints(),
      ]);
      setState(stateData);
      setConfig(configData);
      setEndpoints(endpointsData.endpoints ?? []);
    } catch (e) {
      setLoadError(extractErrorMessage(e, "Falha ao carregar o Digital Twin"));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const runAction = async (label: string, fn: () => Promise<unknown>) => {
    setActionLoading(true);
    setActionError(null);
    setResult(null);
    try {
      const data = await fn();
      setResult({ action: label, ...(data as Record<string, unknown>) });
      await refresh();
    } catch (e) {
      setActionError(extractErrorMessage(e, `Falha ao executar ${label}`));
    } finally {
      setActionLoading(false);
    }
  };

  const healthy = !loadError;

  return (
    <DashboardLayout>
      {/* ─── Header ──────────────────────────────────────────────────── */}
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-500 to-teal-700 text-2xl shadow-lg">
            🧬
          </div>
          <div>
            <h1 className="text-2xl font-bold text-surface-900 dark:text-surface-50">
              Digital Twin
            </h1>
            <p className="mt-0.5 text-sm text-surface-500">
              Estado, ciclo e análise do twin
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant={loading ? "default" : state?.running ? "success" : "warning"} size="md" dot>
            {loading ? "Carregando…" : state?.running ? "Rodando" : "Parado"}
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
          { label: "Rodando", value: state?.running ? "Sim" : "Não", icon: "⚙️" },
          { label: "Ciclos", value: state?.cycles ?? "—", icon: "🔁" },
          { label: "Status do twin", value: state?.twin_status ?? "—", icon: "🧬" },
          { label: "Habilitado", value: config?.enabled ? "Sim" : "Não", icon: "✅" },
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

      {/* ─── Endpoints ───────────────────────────────────────────────── */}
      <Card className="mb-8">
        <CardHeader>
          <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
            Endpoints disponíveis
          </h2>
          <Badge variant="primary" size="sm">{endpoints.length} rotas</Badge>
        </CardHeader>
        <CardBody>
          <div className="flex flex-wrap gap-2">
            {endpoints.length === 0 ? (
              <p className="text-sm text-surface-400">Nenhum endpoint registrado.</p>
            ) : (
              endpoints.map((ep) => (
                <Badge key={ep} variant="default" size="sm">{ep}</Badge>
              ))
            )}
          </div>
        </CardBody>
      </Card>

      {/* ─── Actions ─────────────────────────────────────────────────── */}
      <Card className="mb-8">
        <CardHeader>
          <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
            Ações
          </h2>
          <Badge variant="default" size="sm">Controle do twin</Badge>
        </CardHeader>
        <CardBody>
          <div className="flex flex-wrap gap-2">
            <Button variant="primary" size="sm" onClick={() => void runAction("start", () => digitalTwinApi.start())} isLoading={actionLoading}>
              ▶ Iniciar
            </Button>
            <Button variant="secondary" size="sm" onClick={() => void runAction("stop", () => digitalTwinApi.stop())} isLoading={actionLoading}>
              ⏹ Parar
            </Button>
            <Button variant="secondary" size="sm" onClick={() => void runAction("cycle", () => digitalTwinApi.cycle())} isLoading={actionLoading}>
              🔁 Ciclo
            </Button>
            <div className="flex items-center gap-2">
              <input
                type="number"
                min={1}
                value={steps}
                onChange={(e) => setSteps(Number(e.target.value) || 1)}
                className="w-20 rounded-lg border border-surface-300 bg-white px-2 py-1.5 text-sm text-surface-900 outline-none focus:border-primary-500 dark:border-surface-600 dark:bg-surface-800 dark:text-surface-100"
                aria-label="Passos do tick"
              />
              <Button variant="secondary" size="sm" onClick={() => void runAction("tick", () => digitalTwinApi.tick(steps))} isLoading={actionLoading}>
                ⏱ Tick
              </Button>
            </div>
          </div>

          <div className="mt-4 flex flex-wrap items-center gap-2">
            <input
              value={twinName}
              onChange={(e) => setTwinName(e.target.value)}
              placeholder="Nome do twin"
              className="w-48 rounded-lg border border-surface-300 bg-white px-3 py-1.5 text-sm text-surface-900 outline-none focus:border-primary-500 dark:border-surface-600 dark:bg-surface-800 dark:text-surface-100"
            />
            <Button variant="secondary" size="sm" onClick={() => void runAction("build_twin", () => digitalTwinApi.buildTwin({ name: twinName }))} isLoading={actionLoading}>
              🏗 Construir twin
            </Button>
            <Button variant="secondary" size="sm" onClick={() => void runAction("snapshot", () => digitalTwinApi.snapshot(twinName))} isLoading={actionLoading}>
              📸 Snapshot
            </Button>
            <Button variant="secondary" size="sm" onClick={() => void runAction("analyze", () => digitalTwinApi.analyze({ name: twinName }))} isLoading={actionLoading}>
              🔍 Analisar
            </Button>
            <Button variant="secondary" size="sm" onClick={() => void runAction("validate", () => digitalTwinApi.validate({ name: twinName }))} isLoading={actionLoading}>
              ✔ Validar
            </Button>
          </div>

          {actionError && <p className="mt-3 text-xs text-red-500">{actionError}</p>}
          {result && (
            <pre className="mt-3 max-h-72 overflow-auto rounded-lg bg-surface-100 p-3 text-xs leading-relaxed text-surface-700 dark:bg-surface-800 dark:text-surface-300">
              {JSON.stringify(result, null, 2)}
            </pre>
          )}
        </CardBody>
      </Card>

      {/* ─── Config ──────────────────────────────────────────────────── */}
      <Card className="mb-8">
        <CardHeader>
          <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
            Configuração
          </h2>
          <Badge variant="default" size="sm">Somente leitura</Badge>
        </CardHeader>
        <CardBody>
          <pre className="max-h-72 overflow-auto rounded-lg bg-surface-100 p-3 text-xs leading-relaxed text-surface-700 dark:bg-surface-800 dark:text-surface-300">
            {JSON.stringify(config, null, 2)}
          </pre>
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