"use client";

import Link from "next/link";
import { ControlSection } from "./ControlSection";

const links = [
  { label: "Hub IA", desc: "Digital twin, self-healing, dev autônomo, knowledge graph", icon: "🧩", href: "/intelligence" },
  { label: "Evolução IA", desc: "Motor de evolução contínua", icon: "🌱", href: "/evolution" },
  { label: "Orquestrador", desc: "Filas e tarefas multi-agente", icon: "🎯", href: "/orchestrator" },
  { label: "Agentes", desc: "Agentes e templates", icon: "🤖", href: "/agents" },
  { label: "Workflows", desc: "Automações e pipelines", icon: "⚡", href: "/workflows" },
  { label: "Chat IA", desc: "Conversas com modelos", icon: "💬", href: "/chat" },
  { label: "LLM", desc: "Provedores e modelos", icon: "🧠", href: "/llm" },
  { label: "Runtime", desc: "Execução de código", icon: "💻", href: "/runtime" },
  { label: "Architecture Graph", desc: "Mapa da arquitetura", icon: "🕸️", href: "/architecture-graph" },
  { label: "Arch. Intelligence", desc: "Insights e previsões", icon: "📐", href: "/architecture-intelligence" },
  { label: "Code Search", desc: "Busca semântica no código", icon: "🔍", href: "/code-search" },
  { label: "Code Review", desc: "Revisão automatizada", icon: "🔎", href: "/code-review" },
  { label: "Refactor", desc: "Refatoração assistida", icon: "🔧", href: "/refactor" },
  { label: "Issue → PR", desc: "Gerar PRs de issues", icon: "📬", href: "/issue-to-pr" },
  { label: "Eval Harness", desc: "Avaliação de agentes", icon: "🧪", href: "/eval-harness" },
  { label: "Evals", desc: "Execução de avaliações", icon: "📊", href: "/evals" },
  { label: "MCP", desc: "Servidores MCP", icon: "🔌", href: "/mcp" },
  { label: "Prompt Hub", desc: "Biblioteca de prompts", icon: "📝", href: "/prompt-hub" },
  { label: "Cloud", desc: "VMs e infraestrutura", icon: "☁️", href: "/cloud" },
  { label: "Deploy", desc: "Deploys e ambientes", icon: "🚀", href: "/deploy" },
  { label: "Collab", desc: "Colaboração em tempo real", icon: "👥", href: "/collab" },
  { label: "Memory", desc: "Bases de conhecimento", icon: "🗂️", href: "/memory" },
  { label: "Marketplace", desc: "Plugins disponíveis", icon: "🛍️", href: "/marketplace" },
  { label: "Video Studio", desc: "Geração de vídeos", icon: "🎬", href: "/video-studio" },
  { label: "Command Center", desc: "Central de comandos", icon: "🎛️", href: "/command-center" },
  { label: "Admin", desc: "Administração completa", icon: "🛡️", href: "/admin" },
];

export function ModuleLinksPanel() {
  return (
    <ControlSection
      icon="🧭"
      title="Navegação completa"
      subtitle="Atalhos para todas as ferramentas e módulos"
    >
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
        {links.map((l) => (
          <Link key={l.href} href={l.href} className="group">
            <div className="flex items-center gap-3 rounded-lg border border-surface-100 p-3 transition-all hover:border-primary-300 hover:shadow-sm dark:border-surface-800 dark:hover:border-primary-700">
              <span className="text-lg">{l.icon}</span>
              <div className="min-w-0">
                <p className="truncate text-sm font-medium text-surface-900 group-hover:text-primary-600 dark:text-surface-50 transition-colors">
                  {l.label}
                </p>
                <p className="truncate text-[10px] text-surface-400">{l.desc}</p>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </ControlSection>
  );
}
