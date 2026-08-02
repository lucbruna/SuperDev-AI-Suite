"use client";

import { useEffect, useState } from "react";
import { DashboardLayout } from "@/components/DashboardLayout";
import { settingsApi } from "@/api/settings";
import type { ProviderConfig } from "@/types/settings";

export default function ProvidersPage() {
  const [providers, setProviders] = useState<ProviderConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [selectedProvider, setSelectedProvider] = useState<ProviderConfig | null>(null);
  const [editingApiKey, setEditingApiKey] = useState("");
  const [testingProvider, setTestingProvider] = useState<string | null>(null);
  const [testResults, setTestResults] = useState<Record<string, { success: boolean; message: string }>>({});

  useEffect(() => {
    fetchProviders();
  }, []);

  const fetchProviders = async () => {
    setLoading(true);
    try {
      const data = await settingsApi.getProviderConfigs();
      setProviders(data);
    } catch (err: any) {
      setMessage("Erro ao carregar providers");
    } finally {
      setLoading(false);
    }
  };

  const handleToggleProvider = async (provider: ProviderConfig) => {
    try {
      await settingsApi.updateProviderConfig(provider.id, { enabled: !provider.enabled });
      setProviders(providers.map(p => p.id === provider.id ? { ...p, enabled: !p.enabled } : p));
    } catch (err: any) {
      setMessage("Erro ao atualizar provider");
    }
  };

  const handleSaveApiKey = async (provider: ProviderConfig) => {
    if (!editingApiKey.trim()) return;
    setSaving(true);
    try {
      await settingsApi.updateProviderConfig(provider.id, { apiKey: editingApiKey });
      setMessage(`API key de ${provider.name} salva com sucesso!`);
      setEditingApiKey("");
      setSelectedProvider(null);
      fetchProviders();
    } catch (err: any) {
      setMessage("Erro ao salvar API key");
    } finally {
      setSaving(false);
    }
  };

  const handleTestConnection = async (provider: ProviderConfig) => {
    setTestingProvider(provider.id);
    try {
      const result = await settingsApi.testProviderConnection(provider.id);
      setTestResults({ ...testResults, [provider.id]: result });
    } catch (err: any) {
      setTestResults({ ...testResults, [provider.id]: { success: false, message: "Erro ao testar conexão" } });
    } finally {
      setTestingProvider(null);
    }
  };

  const providerIcons: Record<string, string> = {
    openai: "🟢",
    anthropic: "🟠",
    google: "🔵",
    openrouter: "🟣",
    groq: "⚡",
  };

  return (
    <DashboardLayout>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-surface-900 dark:text-surface-50">Providers de IA</h1>
        <p className="mt-1 text-sm text-surface-500">Configure seus provedores de IA e modelos</p>
      </div>

      {message && (
        <div className={`mb-4 rounded-lg p-3 text-sm ${message.includes("Erro") ? "bg-red-50 text-red-600" : "bg-green-50 text-green-600"}`}>
          {message}
          <button onClick={() => setMessage("")} className="ml-2 text-surface-400 hover:text-surface-600">×</button>
        </div>
      )}

      {loading ? (
        <p className="text-surface-400">Carregando providers...</p>
      ) : (
        <div className="space-y-4">
          {providers.map((provider) => (
            <div
              key={provider.id}
              className="rounded-xl border bg-white p-6 shadow-sm dark:border-surface-700 dark:bg-surface-900"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="text-3xl">{providerIcons[provider.id] || "🔧"}</div>
                  <div>
                    <h3 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
                      {provider.name}
                    </h3>
                    <p className="text-sm text-surface-500">
                      {provider.models.length} modelos disponíveis
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => handleToggleProvider(provider)}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      provider.enabled ? "bg-primary-600" : "bg-surface-300"
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        provider.enabled ? "translate-x-6" : "translate-x-1"
                      }`}
                    />
                  </button>
                </div>
              </div>

              {/* Models */}
              <div className="mt-4">
                <p className="mb-2 text-sm font-medium text-surface-700 dark:text-surface-300">Modelos:</p>
                <div className="flex flex-wrap gap-2">
                  {provider.models.map((model) => (
                    <span
                      key={model}
                      className="rounded-full bg-surface-100 px-3 py-1 text-xs font-medium text-surface-700 dark:bg-surface-800 dark:text-surface-300"
                    >
                      {model}
                    </span>
                  ))}
                </div>
              </div>

              {/* API Key Section */}
              <div className="mt-4 border-t pt-4 dark:border-surface-700">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-surface-700 dark:text-surface-300">
                      API Key
                    </p>
                    <p className="text-xs text-surface-500">
                      {provider.apiKeyConfigured ? (
                        <span className="text-green-600">✓ Configurada</span>
                      ) : (
                        <span className="text-red-500">✗ Não configurada</span>
                      )}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setSelectedProvider(provider)}
                      className="rounded-lg border px-3 py-1.5 text-xs font-medium text-surface-600 hover:bg-surface-50 dark:border-surface-600"
                    >
                      {provider.apiKeyConfigured ? "Atualizar" : "Configurar"}
                    </button>
                    <button
                      onClick={() => handleTestConnection(provider)}
                      disabled={!provider.apiKeyConfigured || testingProvider === provider.id}
                      className="rounded-lg bg-primary-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-primary-700 disabled:opacity-50"
                    >
                      {testingProvider === provider.id ? "Testando..." : "Testar"}
                    </button>
                  </div>
                </div>

                {/* Test Result */}
                {testResults[provider.id] && (
                  <div className={`mt-2 rounded-lg p-2 text-xs ${
                    testResults[provider.id].success
                      ? "bg-green-50 text-green-700"
                      : "bg-red-50 text-red-700"
                  }`}>
                    {testResults[provider.id].message}
                  </div>
                )}
              </div>

              {/* API Key Modal */}
              {selectedProvider?.id === provider.id && (
                <div className="mt-4 rounded-lg border border-primary-200 bg-primary-50 p-4 dark:border-primary-800 dark:bg-primary-900/20">
                  <p className="mb-2 text-sm font-medium text-surface-700 dark:text-surface-300">
                    {provider.apiKeyConfigured ? "Atualizar API Key" : "Configurar API Key"}
                  </p>
                  <div className="flex gap-2">
                    <input
                      type="password"
                      value={editingApiKey}
                      onChange={(e) => setEditingApiKey(e.target.value)}
                      placeholder="Cole sua API key aqui..."
                      className="flex-1 rounded-lg border px-3 py-2 text-sm dark:border-surface-600 dark:bg-surface-800"
                    />
                    <button
                      onClick={() => handleSaveApiKey(provider)}
                      disabled={saving || !editingApiKey.trim()}
                      className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 disabled:opacity-50"
                    >
                      {saving ? "Salvando..." : "Salvar"}
                    </button>
                    <button
                      onClick={() => { setSelectedProvider(null); setEditingApiKey(""); }}
                      className="rounded-lg border px-4 py-2 text-sm font-medium text-surface-600 hover:bg-surface-50 dark:border-surface-600"
                    >
                      Cancelar
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </DashboardLayout>
  );
}
