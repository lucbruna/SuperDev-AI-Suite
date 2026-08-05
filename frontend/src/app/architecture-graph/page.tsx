"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { DashboardLayout } from "@/components/DashboardLayout";
import { Card, CardHeader, CardBody } from "@/components/cards/Card";
import { Badge } from "@/components/badges/Badge";
import { Button } from "@/components/buttons/Button";
import { extractErrorMessage } from "@/utils/apiError";
import {
  architectureGraphApi,
  type GraphStats,
  type InsightItem,
  type SearchResult,
} from "@/api/architectureGraph";

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

const asPct = (v: unknown): number | null => {
  const n = asNum(v);
  return n != null ? Math.round(n * 100) : null;
};

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

const exportFormats = [
  { fmt: "json", label: "JSON" },
  { fmt: "dot", label: "DOT" },
  { fmt: "mermaid", label: "Mermaid" },
  { fmt: "svg", label: "SVG" },
] as const;

const reportKinds = [
  { kind: "architecture", label: "Arquitetura" },
  { kind: "dependency", label: "Dependências" },
  { kind: "html", label: "HTML" },
] as const;

export default function ArchitectureGraphPage() {
  const [version, setVersion] = useState<string>("");
  const [stats, setStats] = useState<GraphStats | null>(null);
  const [analyze, setAnalyze] = useState<Record<string, unknown> | null>(null);
  const [insights, setInsights] = useState<InsightItem[] | null>(null);
  const [risk, setRisk] = useState<InsightItem[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  // Search
  const [query, setQuery] = useState("");
  const [searching, setSearching] = useState(false);
  const [results, setResults] = useState<SearchResult[] | null>(null);
  const [searchError, setSearchError] = useState<string | null>(null);

  // Reports
  const [reportKind, setReportKind] = useState<string>("architecture");
  const [reportLoading, setReportLoading] = useState(false);
  const [reportText, setReportText] = useState<string>("");
  const [reportError, setReportError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const [health, statsData, analyzeData, insightsData, riskData] =
        await Promise.all([
          architectureGraphApi.health(),
          architectureGraphApi.stats(),
          architectureGraphApi.analyze(),
          architectureGraphApi.insights(),
          architectureGraphApi.risk(5),
        ]);
      setVersion(health.version ?? "");
      setStats(statsData);
      setAnalyze(analyzeData);
      setInsights(insightsData.insights ?? null);
      setRisk(riskData.ranking ?? null);
    } catch (e) {
      setLoadError(extractErrorMessage(e, "Falha ao carregar o Architecture Graph"));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setSearching(true);
    setSearchError(null);
    try {
      const data = await architectureGraphApi.search(query.trim());
      setResults(data.results ?? []);
    } catch (e) {
      setSearchError(extractErrorMessage(e, "Falha na busca"));
    } finally {
      setSearching(false);
    }
  };

  const handleReport = async (kind: string) => {
    setReportLoading(true);
    setReportError(null);
    setReportText("");
    try {
      const payload = await architectureGraphApi.report(kind);
      // Reports expose markdown/source text when available; otherwise show JSON.
      const source =
        typeof payload.source === "string"
          ? payload.source
          : typeof payload.markdown === "string"
            ? payload.markdown
            : JSON.stringify(payload, null, 2);
      setReportText(source.slice(0, 12000));
    } catch (e) {
      setReportError(extractErrorMessage(e, "Falha ao gerar relatório"));
    } finally {
      setReportLoading(false);
    }
  };

  // Derived view values (defensive against shape variance).
  const available = stats?.available ?? false;
  const kinds = stats?.kinds ?? {};
  const kindsCount = Object.keys(kinds).length;
  const packages = stats?.layers ? Object.values(stats.layers ?? {}).length : 0;

  const score = (() => {
    const s = analyze?.score;
    if (s && typeof s === "object") {
      const value = (s as Record<string, unknown>).score;
      const n = asNum(value);
      if (n != null) return n;
    }
    return null;
  })();

  const integritySummary = (() => {
    const v = analyze?.integrity_summary;
    return v && typeof v === "object" ? (v as Record<string, number>) : null;
  })();

  const violations = asNum(analyze?.layer_violations);
  const cycles = Array.isArray(analyze?.topological_cycle_ids)
    ? (analyze?.topological_cycle_ids as unknown[]).length
    : 0;

  const healthy = available && !loadError;

  return (
    <DashboardLayout>
      {/* ─── Header ──────────────────────────────────────────────────── */}
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-slate-500 to-primary-700 text-2xl shadow-lg">
            🕸️
          </div>
          <div>
            <h1 className="text-2xl font-bold text-surface-900 dark:text-surface-50">
              Architecture Graph
            </h1>
            <p className="mt-0.5 text-sm text-surface-500">
              Estrutura, saúde e análise do código
              {version ? ` · v${version}` : ""}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant={healthy ? "success" : "danger"} size="md" dot>
            {loading ? "Carregando…" : healthy ? "Backend conectado" : "Backend offline"}
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

      {/* ─── Stats ───────────────────────────────────────────────────── */}
      <div className="mb-8 grid grid-cols-2 gap-3 sm:grid-cols-4">
        {[
          { label: "Nós", value: stats?.nodes ?? "—", icon: "🔹" },
          { label: "Arestas", value: stats?.edges ?? "—", icon: "🔗" },
          { label: "Camadas", value: stats?.layers ? Object.keys(stats.layers).length : "—", icon: "🗂️" },
          { label: "Tipos de nó", value: kindsCount || "—", icon: "🏷️" },
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

      {/* ─── Analysis ────────────────────────────────────────────────── */}
      <Card className="mb-8">
        <CardHeader>
          <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
            Análise da arquitetura
          </h2>
          <Badge variant="primary" size="sm">Análise completa</Badge>
        </CardHeader>
        <CardBody>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-lg border border-surface-200 p-4 text-center dark:border-surface-700">
              <p className="text-3xl font-bold tabular-nums text-surface-900 dark:text-surface-50">
                {score != null ? score.toFixed(1) : "—"}
              </p>
              <p className="text-xs text-surface-500">Score (0–100)</p>
            </div>
            <div className="rounded-lg border border-surface-200 p-4 text-center dark:border-surface-700">
              <p className="text-3xl font-bold tabular-nums text-surface-900 dark:text-surface-50">
                {cycles ?? "—"}
              </p>
              <p className="text-xs text-surface-500">Ciclos de dependência</p>
            </div>
            <div className="rounded-lg border border-surface-200 p-4 text-center dark:border-surface-700">
              <p className="text-3xl font-bold tabular-nums text-surface-900 dark:text-surface-50">
                {violations ?? "—"}
              </p>
              <p className="text-xs text-surface-500">Violações de camada</p>
            </div>
            <div className="rounded-lg border border-surface-200 p-4 text-center dark:border-surface-700">
              <p className="text-3xl font-bold tabular-nums text-surface-900 dark:text-surface-50">
                {integritySummary ? Object.values(integritySummary).reduce((a, b) => a + b, 0) : "—"}
              </p>
              <p className="text-xs text-surface-500">Problemas de integridade</p>
            </div>
          </div>

          {integritySummary && Object.keys(integritySummary).length > 0 && (
            <div className="mt-4 flex flex-wrap gap-2">
              {Object.entries(integritySummary).map(([type, count]) => (
                <Badge key={type} variant="warning" size="sm">
                  {type}: {count}
                </Badge>
              ))}
            </div>
          )}
        </CardBody>
      </Card>

      {/* ─── Insights + Risk ─────────────────────────────────────────── */}
      <div className="mb-8 grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
              Insights
            </h2>
            <Badge variant="primary" size="sm">Detecção automática</Badge>
          </CardHeader>
          <CardBody>
            {insights === null ? (
              <p className="py-4 text-center text-sm text-surface-400">Carregando…</p>
            ) : insights.length === 0 ? (
              <p className="py-4 text-center text-sm text-surface-400">
                Nenhum insight detectado no momento.
              </p>
            ) : (
              <div className="space-y-3">
                {insights.slice(0, 6).map((insight, i) => (
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
              Maiores riscos
            </h2>
            <Badge variant="danger" size="sm">Top 5</Badge>
          </CardHeader>
          <CardBody>
            {risk === null ? (
              <p className="py-4 text-center text-sm text-surface-400">Carregando…</p>
            ) : risk.length === 0 ? (
              <p className="py-4 text-center text-sm text-surface-400">
                Nenhum risco identificado.
              </p>
            ) : (
              <div className="space-y-3">
                {risk.map((item, i) => (
                  <div
                    key={`${item.category}-${i}`}
                    className="rounded-lg border border-surface-100 p-3 dark:border-surface-800"
                  >
                    <div className="flex items-center gap-2">
                      <Badge variant={severityVariant(item.severity)} size="sm" dot>
                        {item.severity ?? "—"}
                      </Badge>
                      {item.category && (
                        <span className="text-[10px] uppercase tracking-wide text-surface-400">
                          {item.category}
                        </span>
                      )}
                    </div>
                    <p className="mt-1.5 text-sm font-medium text-surface-900 dark:text-surface-50">
                      {item.title ?? "Sem título"}
                    </p>
                    {item.detail && (
                      <p className="mt-0.5 text-xs text-surface-500">{item.detail}</p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </CardBody>
        </Card>
      </div>

      {/* ─── Search ──────────────────────────────────────────────────── */}
      <Card className="mb-8">
        <CardHeader>
          <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
            Buscar no grafo
          </h2>
          <Badge variant="default" size="sm">Busca semântica</Badge>
        </CardHeader>
        <CardBody>
          <div className="flex flex-col gap-2 sm:flex-row">
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") void handleSearch();
              }}
              placeholder="Ex.: coupling_analyzer, engine, router…"
              className="w-full rounded-lg border border-surface-300 bg-white px-3 py-2 text-sm text-surface-900 outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 dark:border-surface-600 dark:bg-surface-800 dark:text-surface-100"
            />
            <Button variant="primary" onClick={handleSearch} isLoading={searching} disabled={!query.trim()}>
              Buscar
            </Button>
          </div>
          {searchError && (
            <p className="mt-2 text-xs text-red-500">{searchError}</p>
          )}
          {results !== null && (
            <div className="mt-4 space-y-2">
              {results.length === 0 ? (
                <p className="text-sm text-surface-400">Nenhum resultado para “{query}”.</p>
              ) : (
                results.slice(0, 10).map((r, i) => (
                  <div
                    key={`${r.doc_id ?? r.id ?? i}-${i}`}
                    className="flex items-center justify-between gap-3 rounded-lg border border-surface-100 p-3 dark:border-surface-800"
                  >
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium text-surface-900 dark:text-surface-50">
                        {r.name ?? r.id ?? r.doc_id ?? "—"}
                      </p>
                      {(r.path || r.kind) && (
                        <p className="truncate text-xs text-surface-500">
                          {r.path ?? ""}
                          {r.path && r.kind ? " · " : ""}
                          {r.kind ?? ""}
                        </p>
                      )}
                    </div>
                    {r.score != null && (
                      <Badge variant="info" size="sm">
                        {(r.score * 100).toFixed(0)}%
                      </Badge>
                    )}
                  </div>
                ))
              )}
            </div>
          )}
        </CardBody>
      </Card>

      {/* ─── Export + Reports ────────────────────────────────────────── */}
      <div className="mb-8 grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
              Exportar grafo
            </h2>
            <Badge variant="default" size="sm">Download</Badge>
          </CardHeader>
          <CardBody>
            <p className="mb-3 text-xs text-surface-500">
              Baixa a representação atual do grafo no formato escolhido.
            </p>
            <div className="flex flex-wrap gap-2">
              {exportFormats.map(({ fmt, label }) => (
                <Button
                  key={fmt}
                  variant="secondary"
                  size="sm"
                  onClick={() => window.open(architectureGraphApi.exportUrl(fmt), "_blank")}
                >
                  ⬇ {label}
                </Button>
              ))}
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
              Relatórios
            </h2>
            <Badge variant="default" size="sm">Gerados do grafo</Badge>
          </CardHeader>
          <CardBody>
            <div className="flex flex-col gap-2 sm:flex-row">
              <select
                value={reportKind}
                onChange={(e) => setReportKind(e.target.value)}
                className="w-full rounded-lg border border-surface-300 bg-white px-3 py-2 text-sm text-surface-900 outline-none focus:border-primary-500 dark:border-surface-600 dark:bg-surface-800 dark:text-surface-100"
              >
                {reportKinds.map(({ kind, label }) => (
                  <option key={kind} value={kind}>{label}</option>
                ))}
              </select>
              <Button
                variant="primary"
                onClick={() => void handleReport(reportKind)}
                isLoading={reportLoading}
              >
                Gerar
              </Button>
            </div>
            {reportError && <p className="mt-2 text-xs text-red-500">{reportError}</p>}
            {reportText && (
              <pre className="mt-3 max-h-72 overflow-auto rounded-lg bg-surface-100 p-3 text-xs leading-relaxed text-surface-700 dark:bg-surface-800 dark:text-surface-300">
                {reportText}
              </pre>
            )}
          </CardBody>
        </Card>
      </div>

      {/* ─── Back link ───────────────────────────────────────────────── */}
      <div className="mt-6">
        <Link href="/dashboard" className="text-sm text-primary-600 hover:text-primary-700 dark:text-primary-400">
          ← Voltar ao Dashboard
        </Link>
      </div>
    </DashboardLayout>
  );
}
