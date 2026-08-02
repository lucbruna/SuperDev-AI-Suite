"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { DashboardLayout } from "@/components/DashboardLayout";
import { getAgent, startAgent, stopAgent, updateAgent } from "@/api/agents";
import type { Agent } from "@/types/agent";

interface AgentForm {
  name: string;
  description: string;
  model: string;
  provider: string;
  max_steps: number;
  temperature: number;
  system_prompt: string;
}

const DEFAULT_FORM: AgentForm = {
  name: "",
  description: "",
  model: "",
  provider: "openai",
  max_steps: 10,
  temperature: 0.7,
  system_prompt: "",
};

export default function AgentDetailPage() {
  const { id } = useParams<{ id: string }>() ?? { id: "" };
  const router = useRouter();
  const [agent, setAgent] = useState<Agent | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showEdit, setShowEdit] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState<AgentForm>(DEFAULT_FORM);

  useEffect(() => {
    if (!id) return;
    getAgent(id)
      .then(setAgent)
      .catch((err) => setError(err?.message || "Erro ao carregar agente"))
      .finally(() => setLoading(false));
  }, [id]);

  // Poll for status changes so running/idle transitions show up live.
  useEffect(() => {
    if (!id) return;
    const timer = setInterval(async () => {
      try {
        const updated = await getAgent(id);
        setAgent(updated);
      } catch {
        // silent: transient polling failures should not clobber the page error
      }
    }, 5000);
    return () => clearInterval(timer);
  }, [id]);

  const handleStartStop = async () => {
    if (!agent) return;
    try {
      const updated = agent.status === "running" ? await stopAgent(agent.id) : await startAgent(agent.id);
      setAgent(updated);
    } catch (err: any) {
      setError(err?.message || "Erro ao alterar estado");
    }
  };

  const openEdit = () => {
    if (!agent) return;
    setForm({
      name: agent.name,
      description: agent.description,
      model: agent.model ?? "",
      provider: agent.provider ?? "openai",
      max_steps: agent.max_steps,
      temperature: agent.temperature,
      system_prompt: agent.system_prompt ?? "",
    });
    setError("");
    setShowEdit(true);
  };

  const handleSave = async () => {
    if (!agent || !form.name.trim()) return;
    setSaving(true);
    setError("");
    try {
      const updated = await updateAgent(agent.id, form);
      setAgent(updated);
      setShowEdit(false);
    } catch (err: any) {
      setError(err?.message || "Erro ao salvar agente");
    } finally {
      setSaving(false);
    }
  };

  return (
    <DashboardLayout>
      <button onClick={() => router.push("/agents")} className="mb-4 text-sm text-primary-600 hover:underline">
        ← Voltar para Agentes
      </button>

      {loading && <p className="text-surface-400">Carregando...</p>}
      {error && <p className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-600">{error}</p>}

      {agent && (
        <div className="rounded-xl border bg-white p-8 shadow-sm dark:border-surface-700 dark:bg-surface-900">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-4">
              <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-primary-100 text-2xl text-primary-600">
                🤖
              </div>
              <div>
                <h1 className="text-2xl font-bold text-surface-900 dark:text-surface-50">{agent.name}</h1>
                <p className="mt-1 text-surface-500">{agent.description}</p>
              </div>
            </div>
            <div className="flex gap-2">
              <button
                onClick={openEdit}
                className="rounded-lg border px-4 py-2 text-sm font-medium text-surface-600 hover:bg-surface-50 dark:border-surface-600"
              >
                Editar
              </button>
              <button
                onClick={handleStartStop}
                className={`rounded-lg px-4 py-2 text-sm font-medium text-white ${
                  agent.status === "running"
                    ? "bg-red-500 hover:bg-red-600"
                    : "bg-primary-600 hover:bg-primary-700"
                }`}
              >
                {agent.status === "running" ? "Parar" : "Iniciar"}
              </button>
            </div>
          </div>

          <div className="mt-6 grid grid-cols-2 gap-4 border-t pt-6 dark:border-surface-700">
            <div>
              <p className="text-sm text-surface-500">Tipo</p>
              <p className="font-medium text-surface-900 dark:text-surface-50 capitalize">{agent.agent_type}</p>
            </div>
            <div>
              <p className="text-sm text-surface-500">Status</p>
              <p className="font-medium text-surface-900 dark:text-surface-50 capitalize">{agent.status}</p>
            </div>
            {agent.model && (
              <div>
                <p className="text-sm text-surface-500">Modelo</p>
                <p className="font-medium text-surface-900 dark:text-surface-50">{agent.model}</p>
              </div>
            )}
            {agent.provider && (
              <div>
                <p className="text-sm text-surface-500">Provedor</p>
                <p className="font-medium text-surface-900 dark:text-surface-50">{agent.provider}</p>
              </div>
            )}
            <div>
              <p className="text-sm text-surface-500">Max Steps</p>
              <p className="font-medium text-surface-900 dark:text-surface-50">{agent.max_steps}</p>
            </div>
            <div>
              <p className="text-sm text-surface-500">Temperatura</p>
              <p className="font-medium text-surface-900 dark:text-surface-50">{agent.temperature}</p>
            </div>
          </div>

          {agent.tools && agent.tools.length > 0 && (
            <div className="mt-6 border-t pt-6 dark:border-surface-700">
              <h3 className="mb-3 font-semibold text-surface-900 dark:text-surface-50">Ferramentas</h3>
              <div className="space-y-2">
                {agent.tools.map((tool, i) => (
                  <div key={i} className="rounded-lg bg-surface-50 p-3 text-sm dark:bg-surface-800">
                    <p className="font-medium text-surface-900 dark:text-surface-50">{tool.name}</p>
                    {tool.description && (
                      <p className="mt-1 text-surface-500">{tool.description}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Edit Modal */}
      {showEdit && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-lg rounded-xl bg-white p-6 shadow-xl dark:bg-surface-900">
            <h2 className="mb-4 text-lg font-semibold text-surface-900 dark:text-surface-50">
              Editar Agente
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">Nome</label>
                <input
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  className="mt-1 w-full rounded-lg border px-4 py-2 text-sm dark:border-surface-600 dark:bg-surface-800"
                  placeholder="Nome do agente"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">Descrição</label>
                <input
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                  className="mt-1 w-full rounded-lg border px-4 py-2 text-sm dark:border-surface-600 dark:bg-surface-800"
                  placeholder="O que este agente faz?"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">Provider</label>
                  <select
                    value={form.provider}
                    onChange={(e) => setForm({ ...form, provider: e.target.value })}
                    className="mt-1 w-full rounded-lg border px-4 py-2 text-sm dark:border-surface-600 dark:bg-surface-800"
                  >
                    <option value="openai">OpenAI</option>
                    <option value="anthropic">Anthropic</option>
                    <option value="google">Google</option>
                    <option value="openrouter">OpenRouter</option>
                    <option value="groq">Groq</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">Modelo</label>
                  <input
                    value={form.model}
                    onChange={(e) => setForm({ ...form, model: e.target.value })}
                    className="mt-1 w-full rounded-lg border px-4 py-2 text-sm dark:border-surface-600 dark:bg-surface-800"
                    placeholder="gpt-4"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">
                    Temperatura: {form.temperature}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="2"
                    step="0.1"
                    value={form.temperature}
                    onChange={(e) => setForm({ ...form, temperature: parseFloat(e.target.value) })}
                    className="mt-1 w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">Max Steps</label>
                  <input
                    type="number"
                    min="1"
                    max="50"
                    value={form.max_steps}
                    onChange={(e) => setForm({ ...form, max_steps: parseInt(e.target.value) })}
                    className="mt-1 w-full rounded-lg border px-4 py-2 text-sm dark:border-surface-600 dark:bg-surface-800"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">System Prompt</label>
                <textarea
                  value={form.system_prompt}
                  onChange={(e) => setForm({ ...form, system_prompt: e.target.value })}
                  rows={3}
                  className="mt-1 w-full rounded-lg border px-4 py-2 text-sm dark:border-surface-600 dark:bg-surface-800"
                  placeholder="Instruções para o agente..."
                />
              </div>
            </div>
            <div className="mt-6 flex justify-end gap-3">
              <button
                onClick={() => setShowEdit(false)}
                className="rounded-lg border px-4 py-2 text-sm font-medium text-surface-600 hover:bg-surface-50 dark:border-surface-600"
              >
                Cancelar
              </button>
              <button
                onClick={handleSave}
                disabled={saving || !form.name.trim()}
                className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 disabled:opacity-50"
              >
                {saving ? "Salvando..." : "Salvar Alterações"}
              </button>
            </div>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}
