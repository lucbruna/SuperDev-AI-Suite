"use client";

import { useEffect, useState } from "react";
import { DashboardLayout } from "@/components/DashboardLayout";
import { settingsApi } from "@/api/settings";
import type { LLMSettings, ProviderConfig } from "@/types/settings";

export default function LLMSettingsPage() {
  const [llmSettings, setLlmSettings] = useState<LLMSettings>({
    provider: "openai",
    model: "gpt-4",
    temperature: 0.7,
    max_tokens: 4096,
    system_prompt: "",
  });
  const [providers, setProviders] = useState<ProviderConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [llm, provs] = await Promise.all([
        settingsApi.getLLMSettings(),
        settingsApi.getProviderConfigs(),
      ]);
      setLlmSettings(llm);
      setProviders(provs.filter(p => p.enabled));
    } catch (err: any) {
      setMessage("Erro ao carregar configurações");
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setMessage("");
    try {
      await settingsApi.updateLLMSettings(llmSettings);
      setMessage("Configurações LLM salvas com sucesso!");
    } catch (err: any) {
      setMessage("Erro ao salvar configurações");
    } finally {
      setSaving(false);
    }
  };

  const selectedProvider = providers.find(p => p.id === llmSettings.provider);
  const availableModels = selectedProvider?.models || [];

  return (
    <DashboardLayout>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-surface-900 dark:text-surface-50">Configurações LLM</h1>
        <p className="mt-1 text-sm text-surface-500">Configure o modelo padrão para agentes e chat</p>
      </div>

      {message && (
        <div className={`mb-4 rounded-lg p-3 text-sm ${message.includes("Erro") ? "bg-red-50 text-red-600" : "bg-green-50 text-green-600"}`}>
          {message}
          <button onClick={() => setMessage("")} className="ml-2 text-surface-400 hover:text-surface-600">×</button>
        </div>
      )}

      {loading ? (
        <p className="text-surface-400">Carregando...</p>
      ) : (
        <div className="space-y-6">
          <div className="rounded-xl border bg-white p-6 shadow-sm dark:border-surface-700 dark:bg-surface-900">
            <h2 className="mb-4 text-lg font-semibold text-surface-900 dark:text-surface-50">Modelo Padrão</h2>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">
                  Provider
                </label>
                <select
                  value={llmSettings.provider}
                  onChange={(e) => setLlmSettings({ ...llmSettings, provider: e.target.value, model: "" })}
                  className="mt-1 w-full rounded-lg border px-4 py-2 text-sm dark:border-surface-600 dark:bg-surface-800"
                >
                  {providers.map((p) => (
                    <option key={p.id} value={p.id}>{p.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">
                  Modelo
                </label>
                <select
                  value={llmSettings.model}
                  onChange={(e) => setLlmSettings({ ...llmSettings, model: e.target.value })}
                  className="mt-1 w-full rounded-lg border px-4 py-2 text-sm dark:border-surface-600 dark:bg-surface-800"
                >
                  {availableModels.map((m) => (
                    <option key={m} value={m}>{m}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          <div className="rounded-xl border bg-white p-6 shadow-sm dark:border-surface-700 dark:bg-surface-900">
            <h2 className="mb-4 text-lg font-semibold text-surface-900 dark:text-surface-50">Parâmetros</h2>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">
                  Temperatura: {llmSettings.temperature}
                </label>
                <input
                  type="range"
                  min="0"
                  max="2"
                  step="0.1"
                  value={llmSettings.temperature}
                  onChange={(e) => setLlmSettings({ ...llmSettings, temperature: parseFloat(e.target.value) })}
                  className="mt-1 w-full"
                />
                <p className="mt-1 text-xs text-surface-500">
                  Baixa = mais focado, Alta = mais criativo
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">
                  Max Tokens
                </label>
                <input
                  type="number"
                  min="256"
                  max="128000"
                  step="256"
                  value={llmSettings.max_tokens}
                  onChange={(e) => setLlmSettings({ ...llmSettings, max_tokens: parseInt(e.target.value) })}
                  className="mt-1 w-full rounded-lg border px-4 py-2 text-sm dark:border-surface-600 dark:bg-surface-800"
                />
              </div>
            </div>
          </div>

          <div className="rounded-xl border bg-white p-6 shadow-sm dark:border-surface-700 dark:bg-surface-900">
            <h2 className="mb-4 text-lg font-semibold text-surface-900 dark:text-surface-500">System Prompt Padrão</h2>
            <textarea
              value={llmSettings.system_prompt}
              onChange={(e) => setLlmSettings({ ...llmSettings, system_prompt: e.target.value })}
              rows={4}
              className="w-full rounded-lg border px-4 py-2 text-sm dark:border-surface-600 dark:bg-surface-800"
              placeholder="Instruções padrão para o modelo..."
            />
          </div>

          <button
            onClick={handleSave}
            disabled={saving}
            className="rounded-lg bg-primary-600 px-6 py-2.5 text-sm font-medium text-white hover:bg-primary-700 disabled:opacity-50"
          >
            {saving ? "Salvando..." : "Salvar Configurações"}
          </button>
        </div>
      )}
    </DashboardLayout>
  );
}
