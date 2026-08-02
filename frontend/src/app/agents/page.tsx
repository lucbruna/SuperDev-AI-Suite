"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { DashboardLayout } from "@/components/DashboardLayout";
import {
  getAgents,
  startAgent,
  stopAgent,
  createAgent,
  updateAgent,
  deleteAgent,
  getAgentTemplates,
  type AgentTemplate,
} from "@/api/agents";
import type { Agent } from "@/types/agent";

export default function AgentsPage() {
  const router = useRouter();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [templates, setTemplates] = useState<AgentTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<AgentTemplate | null>(null);
  const [newAgent, setNewAgent] = useState({
    name: "",
    description: "",
    agent_type: "react",
    model: "gpt-4",
    provider: "openai",
    max_steps: 10,
    temperature: 0.7,
    system_prompt: "",
  });
  const [editingAgent, setEditingAgent] = useState<Agent | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError("");
    try {
      const [agentsData, templatesData] = await Promise.all([
        getAgents(),
        getAgentTemplates(),
      ]);
      setAgents(Array.isArray(agentsData) ? agentsData : []);
      setTemplates(Array.isArray(templatesData) ? templatesData : []);
    } catch (err: any) {
      setError(err?.message || "Erro ao carregar agentes");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Lightweight polling so agent status stays current without manual refresh.
  useEffect(() => {
    const timer = setInterval(async () => {
      try {
        const data = await getAgents();
        if (Array.isArray(data)) setAgents(data);
      } catch {
        // silent: transient polling failures should not flash the error banner
      }
    }, 5000);
    return () => clearInterval(timer);
  }, []);

  const handleStartStop = async (agent: Agent) => {
    try {
      if (agent.status === "running") {
        await stopAgent(agent.id);
      } else {
        await startAgent(agent.id);
      }
      fetchData();
    } catch (err: any) {
      setError(err?.message || "Erro ao alterar estado do agente");
    }
  };

  const handleDelete = async (agent: Agent) => {
    if (!confirm(`Excluir agente "${agent.name}"?`)) return;
    try {
      await deleteAgent(agent.id);
      fetchData();
    } catch (err: any) {
      setError(err?.message || "Erro ao excluir agente");
    }
  };

  const handleCreateFromTemplate = (template: AgentTemplate) => {
    setSelectedTemplate(template);
    setNewAgent({
      name: template.name,
      description: template.description,
      agent_type: template.agent_type,
      model: template.model,
      provider: template.provider,
      max_steps: template.max_steps,
      temperature: template.temperature,
      system_prompt: template.system_prompt,
    });
    setShowCreateModal(true);
  };

  const handleCreateCustom = () => {
    setSelectedTemplate(null);
    setNewAgent({
      name: "",
      description: "",
      agent_type: "react",
      model: "gpt-4",
      provider: "openai",
      max_steps: 10,
      temperature: 0.7,
      system_prompt: "",
    });
    setShowCreateModal(true);
  };

  const handleEdit = (agent: Agent) => {
    setSelectedTemplate(null);
    setEditingAgent(agent);
    setNewAgent({
      name: agent.name,
      description: agent.description,
      agent_type: agent.agent_type,
      model: agent.model ?? "gpt-4",
      provider: agent.provider ?? "openai",
      max_steps: agent.max_steps,
      temperature: agent.temperature,
      system_prompt: agent.system_prompt ?? "",
    });
    setShowCreateModal(true);
  };

  const closeModal = () => {
    setShowCreateModal(false);
    setEditingAgent(null);
    setSelectedTemplate(null);
  };

  const handleCreate = async () => {
    if (!newAgent.name.trim()) {
      setError("Nome é obrigatório");
      return;
    }
    try {
      if (editingAgent) {
        await updateAgent(editingAgent.id, newAgent);
      } else {
        await createAgent({
          ...newAgent,
          template_id: selectedTemplate?.id,
        });
      }
      setShowCreateModal(false);
      setEditingAgent(null);
      fetchData();
    } catch (err: any) {
      setError(err?.message || "Erro ao salvar agente");
    }
  };

  const templateCategories = [...new Set(templates.map(t => t.category))];

  return (
    <DashboardLayout>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-surface-900 dark:text-surface-50">Agentes IA</h1>
          <p className="mt-1 text-sm text-surface-500">Gerencie e configure seus agentes inteligentes</p>
        </div>
        <button
          onClick={handleCreateCustom}
          className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700"
        >
          + Criar Agente
        </button>
      </div>

      {error && (
        <div className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-600">
          {error}
          <button onClick={() => setError("")} className="ml-2 text-red-400 hover:text-red-600">×</button>
        </div>
      )}

      {/* Templates Section */}
      <div className="mb-8">
        <h2 className="mb-4 text-lg font-semibold text-surface-900 dark:text-surface-50">Templates Rápidos</h2>
        <div className="space-y-4">
          {templateCategories.map((category) => (
            <div key={category}>
              <h3 className="mb-2 text-sm font-medium text-surface-500">{category}</h3>
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                {templates
                  .filter((t) => t.category === category)
                  .map((template) => (
                    <button
                      key={template.id}
                      onClick={() => handleCreateFromTemplate(template)}
                      className="rounded-xl border bg-white p-4 text-left shadow-sm transition-all hover:border-primary-300 hover:shadow-md dark:border-surface-700 dark:bg-surface-900 dark:hover:border-primary-600"
                    >
                      <div className="mb-2 text-2xl">{template.icon}</div>
                      <h4 className="font-semibold text-surface-900 dark:text-surface-50">{template.name}</h4>
                      <p className="mt-1 text-xs text-surface-500 line-clamp-2">{template.description}</p>
                      <div className="mt-2 flex items-center gap-2">
                        <span className="rounded-full bg-surface-100 px-2 py-0.5 text-xs text-surface-600 dark:bg-surface-800">
                          {template.model}
                        </span>
                      </div>
                    </button>
                  ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Active Agents */}
      <div>
        <h2 className="mb-4 text-lg font-semibold text-surface-900 dark:text-surface-50">Agentes Ativos</h2>
        {loading ? (
          <p className="text-surface-400">Carregando...</p>
        ) : agents.length === 0 ? (
          <div className="rounded-xl border border-dashed bg-white p-8 text-center dark:border-surface-700 dark:bg-surface-900">
            <p className="text-surface-400">Nenhum agente criado ainda.</p>
            <p className="mt-2 text-sm text-surface-500">Use um template acima ou crie um agente personalizado.</p>
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2">
            {agents.map((agent) => (
              <div
                key={agent.id}
                className="rounded-xl border bg-white p-6 shadow-sm dark:border-surface-700 dark:bg-surface-900"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary-100 text-primary-600">
                      🤖
                    </div>
                    <div>
                      <h3 className="font-semibold text-surface-900 dark:text-surface-50">{agent.name}</h3>
                      <p className="text-xs text-surface-500">{agent.agent_type}</p>
                    </div>
                  </div>
                  <span
                    className={`rounded-full px-2 py-1 text-xs font-medium ${
                      agent.status === "running"
                        ? "bg-green-100 text-green-700"
                        : agent.status === "error"
                          ? "bg-red-100 text-red-700"
                          : "bg-surface-100 text-surface-600"
                    }`}
                  >
                    {agent.status}
                  </span>
                </div>
                <p className="mt-3 text-sm text-surface-500">{agent.description || "Sem descrição"}</p>
                <div className="mt-2 flex flex-wrap gap-2">
                  {agent.model && (
                    <span className="rounded-full bg-surface-100 px-2 py-0.5 text-xs text-surface-600 dark:bg-surface-800">
                      {agent.model}
                    </span>
                  )}
                  {agent.temperature !== undefined && (
                    <span className="rounded-full bg-surface-100 px-2 py-0.5 text-xs text-surface-600 dark:bg-surface-800">
                      temp: {agent.temperature}
                    </span>
                  )}
                </div>
                <div className="mt-4 flex gap-2">
                  <button
                    onClick={() => handleStartStop(agent)}
                    className={`rounded-lg px-3 py-1.5 text-xs font-medium text-white ${
                      agent.status === "running"
                        ? "bg-red-500 hover:bg-red-600"
                        : "bg-primary-600 hover:bg-primary-700"
                    }`}
                  >
                    {agent.status === "running" ? "Parar" : "Iniciar"}
                  </button>
                  <button
                    onClick={() => handleEdit(agent)}
                    className="rounded-lg border px-3 py-1.5 text-xs font-medium text-surface-600 hover:bg-surface-50 dark:border-surface-600"
                  >
                    Editar
                  </button>
                  <button
                    onClick={() => handleDelete(agent)}
                    className="rounded-lg border px-3 py-1.5 text-xs font-medium text-red-600 hover:bg-red-50 dark:border-surface-600"
                  >
                    Excluir
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-lg rounded-xl bg-white p-6 shadow-xl dark:bg-surface-900">
            <h2 className="mb-4 text-lg font-semibold text-surface-900 dark:text-surface-50">
              {editingAgent
                ? `Editar Agente: ${editingAgent.name}`
                : selectedTemplate
                  ? `Criar a partir de: ${selectedTemplate.name}`
                  : "Criar Novo Agente"}
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">Nome</label>
                <input
                  value={newAgent.name}
                  onChange={(e) => setNewAgent({ ...newAgent, name: e.target.value })}
                  className="mt-1 w-full rounded-lg border px-4 py-2 text-sm dark:border-surface-600 dark:bg-surface-800"
                  placeholder="Nome do agente"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">Descrição</label>
                <input
                  value={newAgent.description}
                  onChange={(e) => setNewAgent({ ...newAgent, description: e.target.value })}
                  className="mt-1 w-full rounded-lg border px-4 py-2 text-sm dark:border-surface-600 dark:bg-surface-800"
                  placeholder="O que este agente faz?"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">Provider</label>
                  <select
                    value={newAgent.provider}
                    onChange={(e) => setNewAgent({ ...newAgent, provider: e.target.value })}
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
                    value={newAgent.model}
                    onChange={(e) => setNewAgent({ ...newAgent, model: e.target.value })}
                    className="mt-1 w-full rounded-lg border px-4 py-2 text-sm dark:border-surface-600 dark:bg-surface-800"
                    placeholder="gpt-4"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">
                    Temperatura: {newAgent.temperature}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="2"
                    step="0.1"
                    value={newAgent.temperature}
                    onChange={(e) => setNewAgent({ ...newAgent, temperature: parseFloat(e.target.value) })}
                    className="mt-1 w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">Max Steps</label>
                  <input
                    type="number"
                    min="1"
                    max="50"
                    value={newAgent.max_steps}
                    onChange={(e) => setNewAgent({ ...newAgent, max_steps: parseInt(e.target.value) })}
                    className="mt-1 w-full rounded-lg border px-4 py-2 text-sm dark:border-surface-600 dark:bg-surface-800"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">System Prompt</label>
                <textarea
                  value={newAgent.system_prompt}
                  onChange={(e) => setNewAgent({ ...newAgent, system_prompt: e.target.value })}
                  rows={3}
                  className="mt-1 w-full rounded-lg border px-4 py-2 text-sm dark:border-surface-600 dark:bg-surface-800"
                  placeholder="Instruções para o agente..."
                />
              </div>
            </div>
            <div className="mt-6 flex justify-end gap-3">
              <button
                onClick={closeModal}
                className="rounded-lg border px-4 py-2 text-sm font-medium text-surface-600 hover:bg-surface-50 dark:border-surface-600"
              >
                Cancelar
              </button>
              <button
                onClick={handleCreate}
                className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700"
              >
                {editingAgent ? "Salvar Alterações" : "Criar Agente"}
              </button>
            </div>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}
