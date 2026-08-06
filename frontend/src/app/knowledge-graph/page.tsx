"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { DashboardLayout } from "@/components/DashboardLayout";
import { Card, CardHeader, CardBody } from "@/components/cards/Card";
import { Badge } from "@/components/badges/Badge";
import { Button } from "@/components/buttons/Button";
import { extractErrorMessage } from "@/utils/apiError";
import {
  knowledgeGraphApi,
  type KnowledgeStatus,
  type KnowledgeEntityCounts,
  type KnowledgeLanguages,
  type KnowledgeFile,
} from "@/api/knowledgeGraph";

export default function KnowledgeGraphPage() {
  const [status, setStatus] = useState<KnowledgeStatus | null>(null);
  const [entityCounts, setEntityCounts] = useState<KnowledgeEntityCounts | null>(null);
  const [languages, setLanguages] = useState<KnowledgeLanguages | null>(null);
  const [files, setFiles] = useState<KnowledgeFile[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [scanLoading, setScanLoading] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);

  const [projectRoot, setProjectRoot] = useState("");
  const [languageFilter, setLanguageFilter] = useState("");

  const refresh = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const [statusData, countsData, langsData, filesData] = await Promise.all([
        knowledgeGraphApi.status(),
        knowledgeGraphApi.entityCounts(),
        knowledgeGraphApi.languages(),
        knowledgeGraphApi.files(),
      ]);
      setStatus(statusData);
      setEntityCounts(countsData);
      setLanguages(langsData);
      setFiles(filesData.files ?? []);
    } catch (e) {
      setLoadError(extractErrorMessage(e, "Falha ao carregar o Knowledge Graph"));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const runAction = async (label: string, fn: () => Promise<unknown>) => {
    setScanLoading(true);
    setActionError(null);
    setResult(null);
    try {
      const data = await fn();
      setResult({ action: label, ...(data as Record<string, unknown>) });
      await refresh();
    } catch (e) {
      setActionError(extractErrorMessage(e, `Falha ao executar ${label}`));
    } finally {
      setScanLoading(false);
    }
  };

  const loadFiles = async () => {
    setScanLoading(true);
    setActionError(null);
    try {
      const data = await knowledgeGraphApi.files(languageFilter || undefined);
      setFiles(data.files ?? []);
    } catch (e) {
      setActionError(extractErrorMessage(e, "Falha ao carregar arquivos"));
    } finally {
      setScanLoading(false);
    }
  };

  const totalEntities = entityCounts
    ? Object.values(entityCounts).reduce((a, b) => a + b, 0)
    : 0;

  return (
    <DashboardLayout>
      {/* ─── Header ──────────────────────────────────────────────────── */}
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-sky-500 to-blue-700 text-2xl shadow-lg">
            🕸️
          </div>
          <div>
            <h1 className="text-2xl font-bold text-surface-900 dark:text-surface-50">
              AI Code Knowledge Graph
            </h1>
            <p className="mt-0.5 text-sm text-surface-500">
              Grafo de conhecimento do código-fonte
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
          { label: "Estado", value: status?.state ?? "—", icon: "🧭" },
          { label: "Entidades", value: totalEntities, icon: "🔷" },
          { label: "Linguagens", value: languages ? Object.keys(languages).length : "—", icon: "🗂️" },
          { label: "Arquivos", value: files.length, icon: "📄" },
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

      {/* ─── Scan ────────────────────────────────────────────────────── */}
      <Card className="mb-8">
        <CardHeader>
          <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
            Escanear código
          </h2>
          <Badge variant="default" size="sm">Construir grafo</Badge>
        </CardHeader>
        <CardBody>
          <div className="flex flex-wrap items-center gap-2">
            <input
              value={projectRoot}
              onChange={(e) => setProjectRoot(e.target.value)}
              placeholder="Project root (opcional)"
              className="w-72 rounded-lg border border-surface-300 bg-white px-3 py-1.5 text-sm text-surface-900 outline-none focus:border-primary-500 dark:border-surface-600 dark:bg-surface-800 dark:text-surface-100"
            />
            <Button
              variant="primary"
              size="sm"
              onClick={() =>
                void runAction("scan", () => knowledgeGraphApi.scan(projectRoot || undefined))
              }
              isLoading={scanLoading}
            >
              🔎 Escanear
            </Button>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => void runAction("snapshot", () => knowledgeGraphApi.snapshot())}
              isLoading={scanLoading}
            >
              📸 Snapshot
            </Button>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => void runAction("reset", () => knowledgeGraphApi.reset())}
              isLoading={scanLoading}
            >
              ⟲ Reset
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

      {/* ─── Entity counts + languages ──────────────────────────────── */}
      <div className="mb-8 grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
              Entidades
            </h2>
            <Badge variant="primary" size="sm">{totalEntities} total</Badge>
          </CardHeader>
          <CardBody>
            {entityCounts && Object.keys(entityCounts).length > 0 ? (
              <ul className="divide-y divide-surface-200 dark:divide-surface-700">
                {Object.entries(entityCounts).map(([kind, count]) => (
                  <li key={kind} className="flex items-center justify-between py-2">
                    <span className="text-sm text-surface-700 dark:text-surface-200">{kind}</span>
                    <span className="text-sm font-semibold tabular-nums text-surface-900 dark:text-surface-50">
                      {count}
                    </span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-surface-400">Nenhuma entidade indexada.</p>
            )}
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
              Linguagens
            </h2>
            <Badge variant="default" size="sm">Distribuição</Badge>
          </CardHeader>
          <CardBody>
            {languages && Object.keys(languages).length > 0 ? (
              <ul className="divide-y divide-surface-200 dark:divide-surface-700">
                {Object.entries(languages).map(([lang, count]) => (
                  <li key={lang} className="flex items-center justify-between py-2">
                    <span className="text-sm text-surface-700 dark:text-surface-200">{lang}</span>
                    <span className="text-sm font-semibold tabular-nums text-surface-900 dark:text-surface-50">
                      {count}
                    </span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-surface-400">Nenhuma linguagem indexada.</p>
            )}
          </CardBody>
        </Card>
      </div>

      {/* ─── Files ───────────────────────────────────────────────────── */}
      <Card className="mb-8">
        <CardHeader>
          <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
            Arquivos indexados
          </h2>
          <div className="flex items-center gap-2">
            <input
              value={languageFilter}
              onChange={(e) => setLanguageFilter(e.target.value)}
              placeholder="Filtrar por linguagem"
              className="w-44 rounded-lg border border-surface-300 bg-white px-3 py-1.5 text-sm text-surface-900 outline-none focus:border-primary-500 dark:border-surface-600 dark:bg-surface-800 dark:text-surface-100"
            />
            <Button variant="secondary" size="sm" onClick={() => void loadFiles()} isLoading={scanLoading}>
              Filtrar
            </Button>
          </div>
        </CardHeader>
        <CardBody>
          {files.length === 0 ? (
            <p className="text-sm text-surface-400">Nenhum arquivo indexado. Execute um scan.</p>
          ) : (
            <ul className="divide-y divide-surface-200 dark:divide-surface-700">
              {files.slice(0, 50).map((f, i) => (
                <li key={i} className="flex items-center justify-between gap-4 py-2">
                  <span className="truncate text-sm text-surface-700 dark:text-surface-200">
                    {f.path}
                  </span>
                  <Badge variant="default" size="sm">{f.language ?? "—"}</Badge>
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