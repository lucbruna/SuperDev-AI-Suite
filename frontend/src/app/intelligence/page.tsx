"use client";

/**
 * Hub IA — central view over the volume 3 AI modules now exposed through the
 * API: Digital Twin, Self-Healing Engine, Autonomous Developer and AI Code
 * Knowledge Graph. Each card shows live status and quick actions, wired to
 * the module backends mounted under /api/v1/* (see backend/app.py).
 */

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { DashboardLayout } from "@/components/DashboardLayout";
import { Card, CardHeader, CardBody } from "@/components/cards/Card";
import { Badge } from "@/components/badges/Badge";
import { Button } from "@/components/buttons/Button";
import { digitalTwinApi } from "@/api/digitalTwin";
import { selfHealingApi } from "@/api/selfHealing";
import { autonomousDeveloperApi } from "@/api/autonomousDeveloper";
import { knowledgeGraphApi } from "@/api/knowledgeGraph";
import type { KnowledgeLanguages } from "@/api/knowledgeGraph";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function fmtNumber(v: number | undefined | null): string {
  return v === undefined || v === null ? "—" : v.toLocaleString("pt-BR");
}

function SectionSkeleton() {
  return (
    <div className="animate-pulse rounded-lg bg-surface-100 p-4 dark:bg-surface-800">
      <div className="h-4 w-32 rounded bg-surface-200 dark:bg-surface-700" />
      <div className="mt-3 h-8 w-24 rounded bg-surface-200 dark:bg-surface-700" />
    </div>
  );
}

function ModuleCard({
  icon,
  title,
  subtitle,
  statusLabel,
  statusOk,
  children,
  footer,
}: {
  icon: string;
  title: string;
  subtitle: string;
  statusLabel: string;
  statusOk: boolean;
  children?: React.ReactNode;
  footer?: React.ReactNode;
}) {
  return (
    <Card className="flex flex-col">
      <CardHeader>
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-violet-50 text-lg dark:bg-violet-950">
            {icon}
          </div>
          <div>
            <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
              {title}
            </h2>
            <p className="text-xs text-surface-400">{subtitle}</p>
          </div>
        </div>
        <Badge variant={statusOk ? "success" : "default"} size="sm" dot>
          {statusLabel}
        </Badge>
      </CardHeader>
      <CardBody>
        {children}
        {footer && <div className="pt-2">{footer}</div>}
      </CardBody>
    </Card>
  );
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function IntelligencePage() {
  const [digitalTwin, setDigitalTwin] = useState<{ running?: boolean; cycles?: number } | null>(null);
  const [healing, setHealing] = useState<{ cycles?: number; events?: number } | null>(null);
  const [developer, setDeveloper] = useState<{ sessions_active?: number; state?: Record<string, unknown> } | null>(null);
  const [languages, setLanguages] = useState<KnowledgeLanguages | null>(null);
  const [knowledgeState, setKnowledgeState] = useState<string | null>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const refresh = useCallback(async () => {
    try {
      const [dt, sh, ad, lang, kg] = await Promise.all([
        digitalTwinApi.status(),
        selfHealingApi.status(),
        autonomousDeveloperApi.status(),
        knowledgeGraphApi.languages(),
        knowledgeGraphApi.status(),
      ]);
      setDigitalTwin(dt);
      setHealing(sh);
      setDeveloper(ad);
      setLanguages(lang);
      setKnowledgeState(typeof kg.state === "string" ? kg.state : null);
      setError(null);
    } catch {
      setError("Não foi possível carregar o estado dos módulos. Verifique se o backend está rodando.");
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

  const totalLanguageFiles = languages
    ? Object.values(languages).reduce((acc, n) => acc + (n ?? 0), 0)
    : 0;

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-surface-900 dark:text-surface-50">
            Hub IA
          </h1>
          <p className="mt-1 text-sm text-surface-400">
            Módulos de inteligência do SuperDev — Digital Twin, Self-Healing,
            Autonomous Developer e Code Knowledge Graph (Volume 3).
          </p>
        </div>

        {error && (
          <p className="rounded-lg bg-red-50 px-3 py-2 text-xs text-red-700 dark:bg-red-950 dark:text-red-300">
            {error}
          </p>
        )}

        {isLoading ? (
          <div className="grid gap-4 lg:grid-cols-2">
            {Array.from({ length: 4 }).map((_, i) => (
              <SectionSkeleton key={i} />
            ))}
          </div>
        ) : (
          <div className="grid gap-4 lg:grid-cols-2">
            {/* ─── Digital Twin ─────────────────────────────────────── */}
            <ModuleCard
              icon="🪞"
              title="Digital Twin"
              subtitle="Gêmeo digital da plataforma (Volume 3)"
              statusLabel={digitalTwin?.running ? "Rodando" : "Parado"}
              statusOk={Boolean(digitalTwin?.running)}
              footer={
                <div className="flex flex-wrap items-center gap-2">
                  <Button
                    variant="primary"
                    size="sm"
                    isLoading={busy}
                    disabled={Boolean(digitalTwin?.running)}
                    onClick={() => runAction(() => digitalTwinApi.start())}
                  >
                    Iniciar
                  </Button>
                  <Button
                    variant="secondary"
                    size="sm"
                    isLoading={busy}
                    disabled={!digitalTwin?.running}
                    onClick={() => runAction(() => digitalTwinApi.stop())}
                  >
                    Parar
                  </Button>
                  <Button
                    variant="secondary"
                    size="sm"
                    isLoading={busy}
                    onClick={() => runAction(() => digitalTwinApi.cycle())}
                  >
                    Ciclo
                  </Button>
                </div>
              }
            >
              <div className="grid grid-cols-2 gap-3">
                <div className="rounded-lg bg-surface-50 p-3 dark:bg-surface-800">
                  <p className="text-xs text-surface-500">Ciclos</p>
                  <p className="text-xl font-bold text-surface-900 dark:text-surface-50">
                    {fmtNumber(digitalTwin?.cycles)}
                  </p>
                </div>
                <div className="rounded-lg bg-surface-50 p-3 dark:bg-surface-800">
                  <p className="text-xs text-surface-500">Status</p>
                  <p className="text-xl font-bold text-primary-600 dark:text-primary-400">
                    {digitalTwin?.running ? "Ativo" : "Ocioso"}
                  </p>
                </div>
              </div>
            </ModuleCard>

            {/* ─── Self-Healing ─────────────────────────────────────── */}
            <ModuleCard
              icon="🩹"
              title="Self-Healing Engine"
              subtitle="Detecção e recuperação automática (Volume 3)"
              statusLabel={healing ? "Disponível" : "Indisponível"}
              statusOk={Boolean(healing)}
              footer={
                <div className="flex flex-wrap items-center gap-2">
                  <Button
                    variant="primary"
                    size="sm"
                    isLoading={busy}
                    onClick={() =>
                      runAction(() =>
                        selfHealingApi.run({ type: "manual", source: "hub-ia" }),
                      )
                    }
                  >
                    Executar ciclo
                  </Button>
                  <Button
                    variant="secondary"
                    size="sm"
                    isLoading={busy}
                    onClick={() => runAction(() => selfHealingApi.events())}
                  >
                    Eventos
                  </Button>
                </div>
              }
            >
              <div className="grid grid-cols-2 gap-3">
                <div className="rounded-lg bg-surface-50 p-3 dark:bg-surface-800">
                  <p className="text-xs text-surface-500">Ciclos</p>
                  <p className="text-xl font-bold text-surface-900 dark:text-surface-50">
                    {fmtNumber(healing?.cycles)}
                  </p>
                </div>
                <div className="rounded-lg bg-surface-50 p-3 dark:bg-surface-800">
                  <p className="text-xs text-surface-500">Eventos</p>
                  <p className="text-xl font-bold text-surface-900 dark:text-surface-50">
                    {fmtNumber(healing?.events)}
                  </p>
                </div>
              </div>
            </ModuleCard>

            {/* ─── Autonomous Developer ─────────────────────────────── */}
            <ModuleCard
              icon="🤖"
              title="Autonomous Developer"
              subtitle="Execução autônoma de tarefas de código (Volume 3)"
              statusLabel={developer ? "Disponível" : "Indisponível"}
              statusOk={Boolean(developer)}
              footer={
                <div className="flex flex-wrap items-center gap-2">
                  <Button
                    variant="primary"
                    size="sm"
                    isLoading={busy}
                    onClick={() =>
                      runAction(() =>
                        autonomousDeveloperApi.execute({ goal: "analisar o estado do projeto" }),
                      )
                    }
                  >
                    Executar tarefa
                  </Button>
                  <Button
                    variant="secondary"
                    size="sm"
                    isLoading={busy}
                    onClick={() => runAction(() => autonomousDeveloperApi.sessions())}
                  >
                    Sessões
                  </Button>
                </div>
              }
            >
              <div className="grid grid-cols-2 gap-3">
                <div className="rounded-lg bg-surface-50 p-3 dark:bg-surface-800">
                  <p className="text-xs text-surface-500">Sessões ativas</p>
                  <p className="text-xl font-bold text-surface-900 dark:text-surface-50">
                    {fmtNumber(developer?.sessions_active)}
                  </p>
                </div>
                <div className="rounded-lg bg-surface-50 p-3 dark:bg-surface-800">
                  <p className="text-xs text-surface-500">Estado</p>
                  <p className="text-xl font-bold text-primary-600 dark:text-primary-400">
                    {String(developer?.state?.value ?? "—")}
                  </p>
                </div>
              </div>
            </ModuleCard>

            {/* ─── Code Knowledge Graph ─────────────────────────────── */}
            <ModuleCard
              icon="🧠"
              title="Code Knowledge Graph"
              subtitle="Grafo de conhecimento do código (Volume 3)"
              statusLabel={knowledgeState ? knowledgeState : "Sem scan"}
              statusOk={Boolean(languages && totalLanguageFiles > 0)}
              footer={
                <div className="flex flex-wrap items-center gap-2">
                  <Button
                    variant="primary"
                    size="sm"
                    isLoading={busy}
                    onClick={() => runAction(() => knowledgeGraphApi.scan("."))}
                  >
                    Escanear repositório
                  </Button>
                  <Button
                    variant="secondary"
                    size="sm"
                    isLoading={busy}
                    onClick={() => runAction(() => knowledgeGraphApi.snapshot())}
                  >
                    Snapshot
                  </Button>
                </div>
              }
            >
              <div className="grid grid-cols-2 gap-3">
                <div className="rounded-lg bg-surface-50 p-3 dark:bg-surface-800">
                  <p className="text-xs text-surface-500">Arquivos indexados</p>
                  <p className="text-xl font-bold text-surface-900 dark:text-surface-50">
                    {fmtNumber(totalLanguageFiles)}
                  </p>
                </div>
                <div className="rounded-lg bg-surface-50 p-3 dark:bg-surface-800">
                  <p className="text-xs text-surface-500">Linguagens</p>
                  <p className="text-xl font-bold text-primary-600 dark:text-primary-400">
                    {fmtNumber(languages ? Object.keys(languages).length : 0)}
                  </p>
                </div>
              </div>
            </ModuleCard>
          </div>
        )}

        {/* ─── Related pages ────────────────────────────────────────── */}
        <div className="flex flex-wrap gap-2 pt-2">
          <Link href="/architecture-graph" className="text-sm text-primary-600 hover:underline dark:text-primary-400">
            Arquitetura →
          </Link>
          <Link href="/architecture-intelligence" className="text-sm text-primary-600 hover:underline dark:text-primary-400">
            Inteligência de Arquitetura →
          </Link>
          <Link href="/dashboard" className="text-sm text-primary-600 hover:underline dark:text-primary-400">
            Dashboard →
          </Link>
        </div>
      </div>
    </DashboardLayout>
  );
}
