"use client";

/**
 * AI Evolution Engine panel — engine status, integration availability and
 * quick actions (analyze / start / stop), fed by the volume 5 module backend
 * mounted at /api/v1/evolution (see frontend/src/api/evolution.ts).
 */

import { useCallback, useEffect, useState } from "react";
import { Card, CardBody, CardHeader } from "@/components/cards/Card";
import { Badge } from "@/components/badges/Badge";
import { Button } from "@/components/buttons/Button";
import { evolutionApi } from "@/api/evolution";
import type {
  EvolutionDashboard,
  EvolutionIntegrationSummary,
} from "@/api/evolution";

// ---------------------------------------------------------------------------
// Skeleton
// ---------------------------------------------------------------------------

function PanelSkeleton() {
  return (
    <Card className="lg:col-span-3 animate-pulse">
      <CardHeader>
        <div className="h-5 w-40 rounded bg-surface-200 dark:bg-surface-700" />
        <div className="h-6 w-24 rounded-full bg-surface-200 dark:bg-surface-700" />
      </CardHeader>
      <CardBody>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div
              key={i}
              className="h-16 rounded-lg bg-surface-100 dark:bg-surface-800"
            />
          ))}
        </div>
      </CardBody>
    </Card>
  );
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatScore(score: number | undefined): string {
  if (score === undefined || score === null) return "—";
  return `${(score * 100).toFixed(1)}%`;
}

const INTEGRATION_LABELS: Record<string, string> = {
  self_healing: "Self-Healing",
  architecture_graph: "Architecture Graph",
  architecture_intelligence: "Arch. Intelligence",
  knowledge_graph: "Knowledge Graph",
  digital_twin: "Digital Twin",
  autonomous_developer: "Autonomous Dev",
  git: "Git",
  github: "GitHub",
  docker: "Docker",
  kubernetes: "Kubernetes",
  mcp: "MCP",
};

function integrationLabel(name: string): string {
  return INTEGRATION_LABELS[name] ?? name.replace(/_/g, " ");
}

function availableIntegrations(summary?: EvolutionIntegrationSummary): string[] {
  if (!summary) return [];
  return Object.entries(summary)
    .filter(([, value]) => Boolean(value) && value !== "missing")
    .map(([name]) => name);
}

// ---------------------------------------------------------------------------
// Panel
// ---------------------------------------------------------------------------

export function EvolutionPanel({ className }: { className?: string }) {
  const [dashboard, setDashboard] = useState<EvolutionDashboard | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const refresh = useCallback(async () => {
    try {
      const payload = await evolutionApi.dashboard();
      setDashboard(payload);
      setError(null);
    } catch {
      setError("Não foi possível carregar o estado do AI Evolution Engine.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const runAction = useCallback(
    async (action: () => Promise<unknown>) => {
      setBusy(true);
      try {
        await action();
        await refresh();
      } catch {
        setError("Ação falhou. Verifique se o backend está rodando.");
      } finally {
        setBusy(false);
      }
    },
    [refresh],
  );

  if (isLoading && !dashboard) {
    return <PanelSkeleton />;
  }

  const engine = dashboard?.engine;
  const integrations = dashboard?.integrations;
  const available = availableIntegrations(integrations);
  const running = Boolean(engine?.running);

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-violet-50 text-lg dark:bg-violet-950">
            🧬
          </div>
          <div>
            <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
              AI Evolution Engine
            </h2>
            <p className="text-xs text-surface-400">
              Evolução contínua da plataforma (Volume 5)
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant={running ? "success" : "default"} size="sm" dot>
            {running ? "Rodando" : "Parado"}
          </Badge>
        </div>
      </CardHeader>

      <CardBody>
        {error && (
          <p className="rounded-lg bg-red-50 px-3 py-2 text-xs text-red-700 dark:bg-red-950 dark:text-red-300">
            {error}
          </p>
        )}

        {/* Engine metrics */}
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-lg bg-surface-50 p-3 dark:bg-surface-800">
            <p className="text-xs text-surface-500">Ciclos</p>
            <p className="text-xl font-bold text-surface-900 dark:text-surface-50">
              {engine?.cycles ?? 0}
            </p>
          </div>
          <div className="rounded-lg bg-surface-50 p-3 dark:bg-surface-800">
            <p className="text-xs text-surface-500">Score de Análise</p>
            <p className="text-xl font-bold text-primary-600 dark:text-primary-400">
              {formatScore(engine?.last_analysis_score)}
            </p>
          </div>
          <div className="rounded-lg bg-surface-50 p-3 dark:bg-surface-800">
            <p className="text-xs text-surface-500">Recomendações Abertas</p>
            <p className="text-xl font-bold text-surface-900 dark:text-surface-50">
              {engine?.open_recommendations ?? 0}
            </p>
          </div>
          <div className="rounded-lg bg-surface-50 p-3 dark:bg-surface-800">
            <p className="text-xs text-surface-500">Decisões Abertas</p>
            <p className="text-xl font-bold text-surface-900 dark:text-surface-50">
              {engine?.open_decisions ?? 0}
            </p>
          </div>
        </div>

        {/* Integrations */}
        <div>
          <p className="mb-2 text-xs font-medium text-surface-400 uppercase tracking-wider">
            Integrações
          </p>
          <div className="flex flex-wrap gap-2">
            {available.length === 0 ? (
              <span className="text-sm text-surface-400">
                Nenhum módulo irmão detectado
              </span>
            ) : (
              available.map((name) => (
                <span
                  key={name}
                  className="inline-flex items-center gap-1.5 rounded-full bg-green-50 px-2.5 py-1 text-xs font-medium text-green-700 dark:bg-green-950 dark:text-green-300"
                >
                  <span className="h-1.5 w-1.5 rounded-full bg-green-500" />
                  {integrationLabel(name)}
                </span>
              ))
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-wrap items-center gap-2 pt-2">
          <Button
            variant="primary"
            size="sm"
            isLoading={busy}
            onClick={() => runAction(() => evolutionApi.analyze())}
          >
            Analisar agora
          </Button>
          <Button
            variant="secondary"
            size="sm"
            isLoading={busy}
            disabled={running}
            onClick={() => runAction(() => evolutionApi.start())}
          >
            Iniciar
          </Button>
          <Button
            variant="secondary"
            size="sm"
            isLoading={busy}
            disabled={!running}
            onClick={() => runAction(() => evolutionApi.stop())}
          >
            Parar
          </Button>
          <span className="text-xs text-surface-400">
            Ticks: {engine?.ticks ?? 0}
          </span>
        </div>
      </CardBody>
    </Card>
  );
}
