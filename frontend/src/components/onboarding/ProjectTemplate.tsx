"use client";

import { useState } from "react";

const TEMPLATES = [
  { id: "web-app", name: "Web Application", description: "Next.js + FastAPI full-stack app", icon: "🌐", difficulty: "beginner" },
  { id: "api-service", name: "API Service", description: "REST API with FastAPI + PostgreSQL", icon: "⚡", difficulty: "beginner" },
  { id: "ai-agent", name: "AI Agent", description: "Multi-agent system with AI orchestration", icon: "🤖", difficulty: "intermediate" },
  { id: "data-pipeline", name: "Data Pipeline", description: "ETL pipeline with scheduled workflows", icon: "📊", difficulty: "intermediate" },
  { id: "microservices", name: "Microservices", description: "Distributed system with Docker Compose", icon: "🧩", difficulty: "advanced" },
  { id: "blank", name: "Blank Project", description: "Start from scratch", icon: "📁", difficulty: "beginner" },
];

interface ProjectTemplateProps {
  onSelect: (templateId: string) => void;
}

export function ProjectTemplate({ onSelect }: ProjectTemplateProps) {
  const [selected, setSelected] = useState<string>("web-app");

  return (
    <div>
      <h3 className="text-lg font-bold text-surface-900 dark:text-surface-50">Choose a Template</h3>
      <p className="mt-1 text-sm text-surface-600 dark:text-surface-400">Start with a pre-configured project template</p>
      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        {TEMPLATES.map((t) => (
          <div
            key={t.id}
            onClick={() => setSelected(t.id)}
            className={`cursor-pointer rounded-xl border-2 p-4 transition-all ${selected === t.id ? "border-primary-500 bg-primary-50 dark:bg-primary-950" : "border-surface-200 bg-white hover:border-surface-300 dark:border-surface-700 dark:bg-surface-900"}`}
          >
            <div className="flex items-center gap-3">
              <span className="text-2xl">{t.icon}</span>
              <div>
                <p className="font-semibold text-surface-900 dark:text-surface-50">{t.name}</p>
                <p className="text-xs text-surface-500">{t.description}</p>
              </div>
            </div>
            <span className={`mt-2 inline-block rounded px-2 py-0.5 text-xs ${t.difficulty === "beginner" ? "bg-green-100 text-green-700" : t.difficulty === "intermediate" ? "bg-yellow-100 text-yellow-700" : "bg-red-100 text-red-700"}`}>
              {t.difficulty}
            </span>
          </div>
        ))}
      </div>
      <button onClick={() => onSelect(selected)} className="mt-4 w-full rounded-lg bg-primary-600 py-2.5 text-sm font-medium text-white hover:bg-primary-700">
        Create Project
      </button>
    </div>
  );
}