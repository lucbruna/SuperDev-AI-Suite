"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import apiClient from "@/api/client";
import { settingsApi } from "@/api/settings";
import { getAgentTemplates, createAgent, type AgentTemplate } from "@/api/agents";
import type { ProviderConfig } from "@/types/settings";

const STEPS = ["Boas-vindas", "Projeto", "IA", "Agente", "Concluído"];

const providerIcons: Record<string, string> = {
  openai: "🟢",
  anthropic: "🟠",
  google: "🔵",
  openrouter: "🟣",
  groq: "⚡",
};

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  // Project
  const [projectName, setProjectName] = useState("");
  const [projectDesc, setProjectDesc] = useState("");
  const [projectCreated, setProjectCreated] = useState(false);

  // Provider
  const [providers, setProviders] = useState<ProviderConfig[]>([]);
  const [providerId, setProviderId] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [providerSaved, setProviderSaved] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);

  // Agent
  const [templates, setTemplates] = useState<AgentTemplate[]>([]);
  const [agentCreated, setAgentCreated] = useState(false);

  useEffect(() => {
    settingsApi
      .getProviderConfigs()
      .then((data) => setProviders(Array.isArray(data) ? data : []))
      .catch(() => {});
    getAgentTemplates()
      .then((t) => setTemplates(Array.isArray(t) ? t.slice(0, 4) : []))
      .catch(() => {});
  }, []);

  const createProject = async () => {
    if (!projectName.trim()) return;
    setBusy(true);
    setError("");
    try {
      await apiClient.post("/projects", {
        name: projectName.trim(),
        description: projectDesc.trim() || undefined,
      });
      setProjectCreated(true);
      setStep(2);
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || "Erro ao criar projeto");
    } finally {
      setBusy(false);
    }
  };

  const saveProvider = async () => {
    if (!providerId || !apiKey.trim()) return;
    setBusy(true);
    setError("");
    try {
      await settingsApi.updateProviderConfig(providerId, {
        apiKey: apiKey.trim(),
        enabled: true,
      });
      setProviderSaved(true);
      setTestResult(null);
      setStep(3);
    } catch (err: any) {
      setError(err?.message || "Erro ao salvar API key");
    } finally {
      setBusy(false);
    }
  };

  const testProvider = async () => {
    if (!providerId) return;
    setTesting(true);
    setTestResult(null);
    try {
      setTestResult(await settingsApi.testProviderConnection(providerId));
    } catch (err: any) {
      setTestResult({ success: false, message: "Erro ao testar conexão" });
    } finally {
      setTesting(false);
    }
  };

  const createAgentFromTemplate = async (template: AgentTemplate) => {
    setBusy(true);
    setError("");
    try {
      await createAgent({ name: template.name, template_id: template.id });
      setAgentCreated(true);
      setStep(4);
    } catch (err: any) {
      setError(err?.message || "Erro ao criar agente");
    } finally {
      setBusy(false);
    }
  };

  const skip = (next: number) => {
    setError("");
    setStep(next);
  };

  const finish = () => router.push("/dashboard");

  return (
    <div className="flex min-h-screen items-center justify-center bg-surface-50 p-4 dark:bg-surface-950">
      <div className="w-full max-w-xl rounded-xl border bg-white p-8 shadow-lg dark:border-surface-700 dark:bg-surface-900">
        {/* Progress */}
        <div className="mb-8 flex items-center justify-between">
          {STEPS.map((label, i) => (
            <div key={label} className="flex flex-col items-center gap-1">
              <div
                className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-medium ${
                  i < step
                    ? "bg-green-100 text-green-700"
                    : i === step
                      ? "bg-primary-600 text-white"
                      : "bg-surface-100 text-surface-400 dark:bg-surface-800"
                }`}
              >
                {i < step ? "✓" : i + 1}
              </div>
              <span className="hidden text-[10px] text-surface-500 sm:block">{label}</span>
            </div>
          ))}
        </div>

        {error && (
          <div className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-600">
            {error}
            <button onClick={() => setError("")} className="ml-2 text-red-400 hover:text-red-600">×</button>
          </div>
        )}

        {/* Step 0: Welcome */}
        {step === 0 && (
          <div className="text-center">
            <div className="mb-4 text-5xl">🚀</div>
            <h1 className="text-2xl font-bold text-surface-900 dark:text-surface-50">
              Boas-vindas ao SuperDev
            </h1>
            <p className="mt-3 text-sm text-surface-500">
              Em alguns passos você vai configurar seu primeiro projeto, conectar um provedor de IA
              e criar seu primeiro agente. Tudo pode ser alterado depois nas configurações.
            </p>
            <div className="mt-8 flex justify-center gap-3">
              <button
                onClick={() => skip(1)}
                className="rounded-lg border px-5 py-2 text-sm font-medium text-surface-600 hover:bg-surface-50 dark:border-surface-600"
              >
                Pular
              </button>
              <button
                onClick={() => skip(1)}
                className="rounded-lg bg-primary-600 px-6 py-2 text-sm font-medium text-white hover:bg-primary-700"
              >
                Começar
              </button>
            </div>
          </div>
        )}

        {/* Step 1: Project */}
        {step === 1 && (
          <div>
            <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">Criar seu primeiro projeto</h2>
            <p className="mt-1 text-sm text-surface-500">
              Os projetos agrupam agentes, código e configurações. Você pode pular e criar depois.
            </p>
            <div className="mt-5 space-y-4">
              <div>
                <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">Nome do projeto</label>
                <input
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  placeholder="Meu primeiro projeto"
                  className="mt-1 w-full rounded-lg border px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 dark:border-surface-600 dark:bg-surface-800"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">Descrição (opcional)</label>
                <textarea
                  value={projectDesc}
                  onChange={(e) => setProjectDesc(e.target.value)}
                  rows={3}
                  placeholder="O que este projeto faz?"
                  className="mt-1 w-full rounded-lg border px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 dark:border-surface-600 dark:bg-surface-800"
                />
              </div>
            </div>
            <div className="mt-6 flex justify-end gap-3">
              <button
                onClick={() => skip(2)}
                className="rounded-lg border px-4 py-2 text-sm font-medium text-surface-600 hover:bg-surface-50 dark:border-surface-600"
              >
                Pular
              </button>
              <button
                onClick={createProject}
                disabled={busy || !projectName.trim()}
                className="rounded-lg bg-primary-600 px-5 py-2 text-sm font-medium text-white hover:bg-primary-700 disabled:opacity-50"
              >
                {busy ? "Criando..." : "Criar projeto"}
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Provider */}
        {step === 2 && (
          <div>
            <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">Conectar um provedor de IA</h2>
            <p className="mt-1 text-sm text-surface-500">
              Escolha um provedor e cole sua API key. Sem ela, os agentes não conseguem executar.
            </p>
            <div className="mt-5 space-y-4">
              <div>
                <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">Provedor</label>
                <select
                  value={providerId}
                  onChange={(e) => { setProviderId(e.target.value); setTestResult(null); }}
                  className="mt-1 w-full rounded-lg border px-4 py-2 text-sm dark:border-surface-600 dark:bg-surface-800"
                >
                  <option value="">Selecione um provedor</option>
                  {providers.map((p) => (
                    <option key={p.id} value={p.id}>
                      {providerIcons[p.id] || "🔧"} {p.name} {p.apiKeyConfigured ? "(já configurado)" : ""}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">API Key</label>
                <input
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="sk-..."
                  className="mt-1 w-full rounded-lg border px-4 py-2 text-sm dark:border-surface-600 dark:bg-surface-800"
                />
              </div>
              {providerId && (
                <button
                  onClick={testProvider}
                  disabled={testing || !providerId}
                  className="text-sm font-medium text-primary-600 hover:underline disabled:opacity-50"
                >
                  {testing ? "Testando..." : "Testar conexão"}
                </button>
              )}
              {testResult && (
                <div className={`rounded-lg p-2 text-xs ${testResult.success ? "bg-green-50 text-green-700" : "bg-red-50 text-red-700"}`}>
                  {testResult.message}
                </div>
              )}
            </div>
            <div className="mt-6 flex justify-end gap-3">
              <button
                onClick={() => skip(3)}
                className="rounded-lg border px-4 py-2 text-sm font-medium text-surface-600 hover:bg-surface-50 dark:border-surface-600"
              >
                Pular
              </button>
              <button
                onClick={saveProvider}
                disabled={busy || !providerId || !apiKey.trim()}
                className="rounded-lg bg-primary-600 px-5 py-2 text-sm font-medium text-white hover:bg-primary-700 disabled:opacity-50"
              >
                {busy ? "Salvando..." : "Salvar e continuar"}
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Agent */}
        {step === 3 && (
          <div>
            <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">Criar um agente (opcional)</h2>
            <p className="mt-1 text-sm text-surface-500">
              Os agentes executam tarefas usando seu provedor de IA. Escolha um modelo para começar.
            </p>
            {templates.length === 0 ? (
              <p className="mt-5 text-sm text-surface-400">Nenhum template disponível no momento.</p>
            ) : (
              <div className="mt-5 grid gap-3 sm:grid-cols-2">
                {templates.map((template) => (
                  <button
                    key={template.id}
                    onClick={() => createAgentFromTemplate(template)}
                    disabled={busy}
                    className="rounded-xl border bg-surface-50 p-4 text-left transition-all hover:border-primary-300 hover:shadow-md disabled:opacity-50 dark:border-surface-700 dark:bg-surface-800"
                  >
                    <div className="mb-2 text-2xl">{template.icon}</div>
                    <h3 className="font-semibold text-surface-900 dark:text-surface-50">{template.name}</h3>
                    <p className="mt-1 text-xs text-surface-500 line-clamp-2">{template.description}</p>
                  </button>
                ))}
              </div>
            )}
            <div className="mt-6 flex justify-end gap-3">
              <button
                onClick={() => skip(4)}
                className="rounded-lg border px-4 py-2 text-sm font-medium text-surface-600 hover:bg-surface-50 dark:border-surface-600"
              >
                Pular
              </button>
            </div>
          </div>
        )}

        {/* Step 4: Done */}
        {step === 4 && (
          <div className="text-center">
            <div className="mb-4 text-5xl">🎉</div>
            <h2 className="text-xl font-bold text-surface-900 dark:text-surface-50">
              {projectCreated ? "Projeto criado!" : "Tudo pronto!"}
            </h2>
            <ul className="mx-auto mt-5 max-w-sm space-y-2 text-left text-sm text-surface-600 dark:text-surface-400">
              <li className="flex items-center gap-2">
                <span className={projectCreated ? "text-green-600" : "text-surface-400"}>{projectCreated ? "✓" : "—"}</span>
                {projectCreated ? `Projeto "${projectName}" criado` : "Nenhum projeto criado"}
              </li>
              <li className="flex items-center gap-2">
                <span className={providerSaved ? "text-green-600" : "text-surface-400"}>{providerSaved ? "✓" : "—"}</span>
                {providerSaved ? "Provedor de IA configurado" : "Provedor de IA não configurado"}
              </li>
              <li className="flex items-center gap-2">
                <span className={agentCreated ? "text-green-600" : "text-surface-400"}>{agentCreated ? "✓" : "—"}</span>
                {agentCreated ? "Agente criado" : "Nenhum agente criado"}
              </li>
            </ul>
            <button
              onClick={finish}
              className="mt-8 rounded-lg bg-primary-600 px-6 py-2 text-sm font-medium text-white hover:bg-primary-700"
            >
              Ir para o Dashboard
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
