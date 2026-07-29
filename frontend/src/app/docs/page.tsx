"use client";

import { useEffect, useState } from "react";
import { DashboardLayout } from "@/components/DashboardLayout";

interface DocModule {
  id: string;
  name: string;
  description: string;
  category: string;
  path: string;
}

export default function DocsPage() {
  const [modules, setModules] = useState<DocModule[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<DocModule | null>(null);

  useEffect(() => {
    fetch("/api/v1/health")
      .then(() => {
        setModules([
          { id: "1", name: "Autenticação", description: "Login, registro, JWT, OAuth2, refresh tokens", category: "auth", path: "/docs/auth" },
          { id: "2", name: "Projetos", description: "CRUD de projetos, membros, estatísticas", category: "projects", path: "/docs/projects" },
          { id: "3", name: "Agentes", description: "Gerenciamento de agentes, execução, status", category: "agents", path: "/docs/agents" },
          { id: "4", name: "API REST", description: "Endpoints da API v1, schemas, exemplos", category: "api", path: "/docs/api" },
          { id: "5", name: "WebSocket", description: "Conexões em tempo real, eventos, salas", category: "realtime", path: "/docs/ws" },
          { id: "6", name: "Deploy", description: "Pipeline de deploy, ambientes, estratégias", category: "deploy", path: "/docs/deploy" },
          { id: "7", name: "Workflows", description: "Automação de fluxos de trabalho", category: "workflows", path: "/docs/workflows" },
          { id: "8", name: "Marketplace", description: "Plugins, instalação, configuração", category: "plugins", path: "/docs/plugins" },
        ]);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const filtered = modules.filter((m) =>
    m.name.toLowerCase().includes(search.toLowerCase()) ||
    m.description.toLowerCase().includes(search.toLowerCase())
  );

  const categoryColors: Record<string, string> = {
    auth: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300",
    projects: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300",
    agents: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300",
    api: "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300",
    realtime: "bg-cyan-100 text-cyan-700 dark:bg-cyan-900/30 dark:text-cyan-300",
    deploy: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300",
    workflows: "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-300",
    plugins: "bg-pink-100 text-pink-700 dark:bg-pink-900/30 dark:text-pink-300",
  };

  return (
    <DashboardLayout>
      <div className="space-y-6 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-surface-900 dark:text-white">Documentação</h1>
            <p className="text-surface-500">Módulos e referências da plataforma</p>
          </div>
          <input
            type="text"
            placeholder="Buscar docs..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="rounded-lg border px-4 py-2 text-sm dark:border-surface-600 dark:bg-surface-800 w-64"
          />
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary-500 border-t-transparent" />
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {filtered.map((mod) => (
              <button
                key={mod.id}
                onClick={() => setSelected(mod)}
                className={`rounded-lg border bg-white p-4 text-left transition hover:shadow-md dark:border-surface-700 dark:bg-surface-900 ${
                  selected?.id === mod.id ? "ring-2 ring-primary-500" : ""
                }`}
              >
                <span className={`inline-block rounded px-2 py-0.5 text-[10px] font-medium ${categoryColors[mod.category] || "bg-surface-100 text-surface-600"}`}>
                  {mod.category}
                </span>
                <h3 className="mt-2 font-semibold text-surface-900 dark:text-surface-50">{mod.name}</h3>
                <p className="mt-1 text-xs text-surface-500">{mod.description}</p>
              </button>
            ))}
          </div>
        )}

        {selected && (
          <div className="rounded-lg border bg-white p-6 dark:border-surface-700 dark:bg-surface-900">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-surface-900 dark:text-white">{selected.name}</h2>
              <button onClick={() => setSelected(null)} className="text-sm text-surface-400 hover:text-surface-600">Fechar</button>
            </div>
            <p className="text-sm text-surface-600 dark:text-surface-400 mb-4">{selected.description}</p>
            <div className="rounded-lg bg-surface-50 p-4 dark:bg-surface-800">
              <p className="text-sm font-mono text-surface-500">Path: {selected.path}</p>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
