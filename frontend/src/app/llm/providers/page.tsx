"use client";

import { useEffect, useState, useCallback } from "react";
import { DashboardLayout } from "@/components/DashboardLayout";
import { llmApi, type LLMProviderSummary, type LLMProviderDetail } from "@/api/llm";

// ---------------------------------------------------------------------------
// Status Badge
// ---------------------------------------------------------------------------

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    healthy: "bg-green-500/10 text-green-400 border-green-500/20",
    unhealthy: "bg-red-500/10 text-red-400 border-red-500/20",
    not_configured: "bg-yellow-500/10 text-yellow-400 border-yellow-500/20",
    error: "bg-red-500/10 text-red-400 border-red-500/20",
  };
  const labels: Record<string, string> = {
    healthy: "Online",
    unhealthy: "Offline",
    not_configured: "Sem chave",
    error: "Erro",
  };

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium ${colors[status] || "bg-gray-500/10 text-gray-400 border-gray-500/20"}`}>
      <span className={`h-1.5 w-1.5 rounded-full ${status === "healthy" ? "bg-green-400 animate-pulse" : "bg-gray-400"}`} />
      {labels[status] || status}
    </span>
  );
}

// ---------------------------------------------------------------------------
// Provider Card
// ---------------------------------------------------------------------------

function ProviderCard({
  summary,
  onTest,
  onViewDetail,
  testing,
}: {
  summary: LLMProviderSummary;
  onTest: (name: string) => void;
  onViewDetail: (name: string) => void;
  testing: string | null;
}) {
  const nameCapitalized = summary.name.charAt(0).toUpperCase() + summary.name.slice(1);

  const providerIcons: Record<string, string> = {
    openai: "🟢",
    anthropic: "🟣",
    google: "🔵",
    deepseek: "🟠",
    groq: "⚡",
    mistral: "💠",
    together: "🔶",
    azure: "🔷",
    aws: "🟠",
    cohere: "🔵",
    huggingface: "❤️",
    local: "💻",
    mock: "🧪",
    custom: "🔧",
  };

  return (
    <div className="rounded-xl border bg-white p-5 shadow-sm transition-all hover:shadow-md dark:border-surface-700 dark:bg-surface-900">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <span className="text-2xl">{providerIcons[summary.name] || "🤖"}</span>
          <div>
            <h3 className="font-semibold text-surface-900 dark:text-surface-50">{nameCapitalized}</h3>
            <p className="text-xs text-surface-500 dark:text-surface-400">{summary.name}</p>
          </div>
        </div>
        <StatusBadge status={summary.api_key_configured ? "healthy" : "not_configured"} />
      </div>

      <div className="mt-4 flex items-center gap-2">
        <button
          onClick={() => onViewDetail(summary.name)}
          className="flex-1 rounded-lg border border-surface-200 px-3 py-2 text-xs font-medium text-surface-600 transition-colors hover:bg-surface-50 dark:border-surface-600 dark:text-surface-300 dark:hover:bg-surface-800"
        >
          Detalhes
        </button>
        <button
          onClick={() => onTest(summary.name)}
          disabled={!summary.api_key_configured || testing === summary.name}
          className="flex-1 rounded-lg bg-primary-600 px-3 py-2 text-xs font-medium text-white transition-colors hover:bg-primary-700 disabled:opacity-50"
        >
          {testing === summary.name ? "Testando..." : "Testar"}
        </button>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Provider Detail Modal
// ---------------------------------------------------------------------------

function ProviderDetailModal({
  name,
  onClose,
}: {
  name: string;
  onClose: () => void;
}) {
  const [detail, setDetail] = useState<LLMProviderDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    llmApi
      .getProvider(name)
      .then(setDetail)
      .catch((err) => setError(err?.message || "Falha ao carregar detalhes"))
      .finally(() => setLoading(false));
  }, [name]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" onClick={onClose}>
      <div className="mx-4 w-full max-w-lg rounded-xl border bg-white p-6 shadow-xl dark:border-surface-700 dark:bg-surface-900" onClick={(e) => e.stopPropagation()}>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-bold text-surface-900 dark:text-surface-50">
            {name.charAt(0).toUpperCase() + name.slice(1)}
          </h2>
          <button onClick={onClose} className="rounded-lg p-1.5 text-surface-400 hover:bg-surface-100 dark:hover:bg-surface-800">
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {loading && (
          <div className="flex items-center justify-center py-8">
            <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary-500 border-t-transparent" />
          </div>
        )}

        {error && (
          <div className="rounded-lg bg-red-500/10 p-4 text-sm text-red-400">{error}</div>
        )}

        {detail && !loading && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-surface-500">Classe</p>
                <p className="text-sm font-medium text-surface-900 dark:text-surface-50">{detail.class}</p>
              </div>
              <div>
                <p className="text-xs text-surface-500">Modelo padrão</p>
                <p className="text-sm font-medium text-surface-900 dark:text-surface-50">{detail.default_model}</p>
              </div>
              <div>
                <p className="text-xs text-surface-500">Env var</p>
                <p className="text-sm font-mono text-surface-900 dark:text-surface-50">{detail.api_key_env_var}</p>
              </div>
              <div>
                <p className="text-xs text-surface-500">Configured</p>
                <StatusBadge status={detail.api_key_configured ? "healthy" : "not_configured"} />
              </div>
            </div>

            {detail.models.length > 0 && (
              <div>
                <p className="mb-2 text-xs font-medium text-surface-500 uppercase tracking-wider">Modelos</p>
                <div className="max-h-48 space-y-1 overflow-y-auto">
                  {detail.models.map((m) => (
                    <div key={m.id} className="rounded-lg border border-surface-100 bg-surface-50 p-2 dark:border-surface-700 dark:bg-surface-800/50">
                      <p className="text-sm font-medium text-surface-900 dark:text-surface-50">{m.id}</p>
                      <div className="mt-1 flex flex-wrap gap-1">
                        {(m.capabilities || []).map((cap) => (
                          <span key={cap} className="rounded-full bg-primary-500/10 px-2 py-0.5 text-xs text-primary-400">
                            {cap}
                          </span>
                        ))}
                        {m.context_window && (
                          <span className="rounded-full bg-surface-500/10 px-2 py-0.5 text-xs text-surface-400">
                            {m.context_window.toLocaleString()} ctx
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main Page
// ---------------------------------------------------------------------------

export default function LLMProvidersPage() {
  const [providers, setProviders] = useState<LLMProviderSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [testing, setTesting] = useState<string | null>(null);
  const [testResult, setTestResult] = useState<{ name: string; status: string; latency?: number } | null>(null);
  const [detailName, setDetailName] = useState<string | null>(null);

  const loadProviders = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await llmApi.listProviders();
      setProviders(data);
    } catch (err: any) {
      setError(err?.message || "Falha ao carregar providers");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadProviders();
  }, [loadProviders]);

  const handleTest = async (name: string) => {
    setTesting(name);
    setTestResult(null);
    try {
      const result = await llmApi.testProvider(name);
      setTestResult({ name, status: result.status, latency: result.latency_ms });
      // Refresh the list after test
      loadProviders();
    } catch (err: any) {
      setTestResult({ name, status: "error", latency: undefined });
    } finally {
      setTesting(null);
    }
  };

  const configuredCount = providers.filter((p) => p.api_key_configured).length;

  return (
    <DashboardLayout>
      <div className="space-y-6 p-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-surface-900 dark:text-white">LLM Providers</h1>
            <p className="mt-1 text-sm text-surface-500">
              {configuredCount} de {providers.length} providers configurados
            </p>
          </div>
          <button
            onClick={loadProviders}
            disabled={loading}
            className="rounded-lg border border-surface-200 px-4 py-2 text-sm font-medium text-surface-600 transition-colors hover:bg-surface-50 dark:border-surface-600 dark:text-surface-300 dark:hover:bg-surface-800 disabled:opacity-50"
          >
            {loading ? "Atualizando..." : "Atualizar"}
          </button>
        </div>

        {/* Test result toast */}
        {testResult && (
          <div
            className={`rounded-lg border p-4 text-sm ${
              testResult.status === "healthy"
                ? "border-green-500/20 bg-green-500/10 text-green-400"
                : "border-red-500/20 bg-red-500/10 text-red-400"
            }`}
          >
            <span className="font-medium">{testResult.name}:</span>{" "}
            {testResult.status === "healthy"
              ? `Conexão OK (${testResult.latency?.toFixed(0)}ms)`
              : "Falha na conexão"}
            <button
              onClick={() => setTestResult(null)}
              className="ml-3 underline opacity-70 hover:opacity-100"
            >
              Fechar
            </button>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="rounded-lg border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-400">
            {error}
            <button onClick={loadProviders} className="ml-3 underline">
              Tentar novamente
            </button>
          </div>
        )}

        {/* Provider grid */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="flex flex-col items-center gap-3">
              <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary-500 border-t-transparent" />
              <p className="text-sm text-surface-400">Carregando providers...</p>
            </div>
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {providers.map((p) => (
              <ProviderCard
                key={p.name}
                summary={p}
                onTest={handleTest}
                onViewDetail={setDetailName}
                testing={testing}
              />
            ))}
          </div>
        )}
      </div>

      {/* Detail modal */}
      {detailName && <ProviderDetailModal name={detailName} onClose={() => setDetailName(null)} />}
    </DashboardLayout>
  );
}
