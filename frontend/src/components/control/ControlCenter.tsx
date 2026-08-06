"use client";

import { useState, type ReactNode } from "react";
import { cn } from "@/utils/cn";
import { OrchestratorPanel } from "./OrchestratorPanel";
import { SystemPanel } from "./SystemPanel";
import { AiModulesPanel } from "./AiModulesPanel";
import { AutomationPanel } from "./AutomationPanel";
import { OpsPanel } from "./OpsPanel";
import { ModuleLinksPanel } from "./ModuleLinksPanel";

interface TabDef {
  id: string;
  label: string;
  icon: string;
  content: ReactNode;
}

const tabs: TabDef[] = [
  { id: "orchestrator", label: "Orquestrador", icon: "🎯", content: <OrchestratorPanel /> },
  { id: "system", label: "Sistema", icon: "🖥️", content: <SystemPanel /> },
  { id: "ai", label: "Módulos IA", icon: "🧠", content: <AiModulesPanel /> },
  { id: "automation", label: "Automação", icon: "⚙️", content: <AutomationPanel /> },
  { id: "ops", label: "Operações", icon: "🗄️", content: <OpsPanel /> },
  { id: "links", label: "Navegação", icon: "🧭", content: <ModuleLinksPanel /> },
];

export function ControlCenter() {
  const [active, setActive] = useState("orchestrator");
  const current = tabs.find((t) => t.id === active) ?? tabs[0];

  return (
    <section className="mb-8">
      <header className="mb-4">
        <div className="flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-primary-600 to-violet-600 text-lg shadow-sm">
            🎛️
          </span>
          <div>
            <h2 className="text-xl font-bold text-surface-900 dark:text-surface-50">
              Centro de Controle
            </h2>
            <p className="text-sm text-surface-500 dark:text-surface-400">
              Opere todos os módulos do SuperDev diretamente do dashboard
            </p>
          </div>
        </div>
      </header>

      <div className="mb-4 flex gap-1.5 overflow-x-auto rounded-xl border border-surface-200 bg-surface-50 p-1.5 dark:border-surface-700 dark:bg-surface-800/60">
        {tabs.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => setActive(t.id)}
            className={cn(
              "flex shrink-0 items-center gap-1.5 rounded-lg px-3.5 py-2 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500",
              active === t.id
                ? "bg-white text-primary-700 shadow-sm dark:bg-surface-900 dark:text-primary-300"
                : "text-surface-600 hover:text-surface-900 hover:bg-white/60 dark:text-surface-400 dark:hover:text-surface-100 dark:hover:bg-surface-800",
            )}
          >
            <span className="text-base">{t.icon}</span>
            {t.label}
          </button>
        ))}
      </div>

      {current.content}
    </section>
  );
}
