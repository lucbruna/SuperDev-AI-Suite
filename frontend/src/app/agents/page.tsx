"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { DashboardLayout } from "@/components/DashboardLayout";
import { getAgents, startAgent, stopAgent } from "@/api/agents";

interface AgentItem {
  id: string;
  name: string;
  description: string;
  status: string;
  agent_type?: string;
}

export default function AgentsPage() {
  const router = useRouter();
  const [agents, setAgents] = useState<AgentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchAgents = () => {
    setLoading(true);
    setError("");
    getAgents()
      .then((data: any) => setAgents(Array.isArray(data) ? data : []))
      .catch((err) => setError(err?.message || "Erro ao carregar agentes"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchAgents();
  }, []);

  const handleStartStop = async (agent: AgentItem) => {
    try {
      if (agent.status === "running") {
        await stopAgent(agent.id);
      } else {
        await startAgent(agent.id);
      }
      fetchAgents();
    } catch (err: any) {
      setError(err?.message || "Erro ao alterar estado do agente");
    }
  };

  return (
    <DashboardLayout>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-surface-900 dark:text-surface-50">Agentes IA</h1>
        <p className="mt-1 text-sm text-surface-500">Gerencie seus agentes inteligentes</p>
      </div>

      {loading && <p className="text-surface-400">Carregando...</p>}
      {error && <p className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-600">{error}</p>}

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
                  <p className="text-xs text-surface-500">{agent.agent_type || "react"}</p>
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
            <p className="mt-3 text-sm text-surface-500">{agent.description}</p>
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
                onClick={() => router.push(`/agents/${agent.id}`)}
                className="rounded-lg border px-3 py-1.5 text-xs font-medium text-surface-600 hover:bg-surface-50 dark:border-surface-600 dark:text-surface-400"
              >
                Configurar
              </button>
            </div>
          </div>
        ))}
        {!loading && agents.length === 0 && (
          <p className="col-span-full text-center text-surface-400">Nenhum agente disponível.</p>
        )}
      </div>
    </DashboardLayout>
  );
}
