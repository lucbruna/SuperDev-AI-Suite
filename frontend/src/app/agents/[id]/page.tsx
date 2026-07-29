"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { DashboardLayout } from "@/components/DashboardLayout";
import { getAgent, startAgent, stopAgent } from "@/api/agents";

export default function AgentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [agent, setAgent] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!id) return;
    getAgent(id)
      .then(setAgent)
      .catch((err) => setError(err?.message || "Erro ao carregar agente"))
      .finally(() => setLoading(false));
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
          </div>

          {agent.tools && agent.tools.length > 0 && (
            <div className="mt-6 border-t pt-6 dark:border-surface-700">
              <h3 className="mb-3 font-semibold text-surface-900 dark:text-surface-50">Ferramentas</h3>
              <div className="space-y-2">
                {agent.tools.map((tool: any, i: number) => (
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
    </DashboardLayout>
  );
}
