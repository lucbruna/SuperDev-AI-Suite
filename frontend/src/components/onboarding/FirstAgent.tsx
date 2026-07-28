"use client";

import { useState } from "react";

interface FirstAgentProps {
  onComplete: (config: { name: string; type: string; model: string }) => void;
}

const AGENT_TYPES = [
  { id: "assistant", name: "Assistant", description: "General purpose AI assistant", icon: "💬" },
  { id: "coder", name: "Coder", description: "Code generation and review", icon: "💻" },
  { id: "reviewer", name: "Reviewer", description: "Code review and quality checks", icon: "🔍" },
  { id: "deployer", name: "Deployer", description: "Deployment automation", icon: "🚀" },
];

export function FirstAgent({ onComplete }: FirstAgentProps) {
  const [name, setName] = useState("My First Agent");
  const [type, setType] = useState("assistant");
  const [model, setModel] = useState("gpt-4o");

  return (
    <div>
      <h3 className="text-lg font-bold text-surface-900 dark:text-surface-50">Create Your First Agent</h3>
      <p className="mt-1 text-sm text-surface-600 dark:text-surface-400">Give your agent a name and choose its role</p>
      <div className="mt-4 space-y-4">
        <div>
          <label className="text-sm font-medium text-surface-700 dark:text-surface-300">Agent Name</label>
          <input type="text" value={name} onChange={(e) => setName(e.target.value)} className="mt-1 w-full rounded-lg border border-surface-300 bg-white px-3 py-2 text-sm dark:border-surface-600 dark:bg-surface-800 dark:text-surface-100" />
        </div>
        <div>
          <label className="text-sm font-medium text-surface-700 dark:text-surface-300">Agent Type</label>
          <div className="mt-1 grid grid-cols-2 gap-2">
            {AGENT_TYPES.map((t) => (
              <div key={t.id} onClick={() => setType(t.id)} className={`cursor-pointer rounded-lg border-2 p-3 text-center ${type === t.id ? "border-primary-500 bg-primary-50 dark:bg-primary-950" : "border-surface-200 bg-white dark:border-surface-700 dark:bg-surface-900"}`}>
                <span className="text-2xl">{t.icon}</span>
                <p className="text-sm font-medium text-surface-900 dark:text-surface-50">{t.name}</p>
                <p className="text-xs text-surface-500">{t.description}</p>
              </div>
            ))}
          </div>
        </div>
        <div>
          <label className="text-sm font-medium text-surface-700 dark:text-surface-300">Model</label>
          <select value={model} onChange={(e) => setModel(e.target.value)} className="mt-1 w-full rounded-lg border border-surface-300 bg-white px-3 py-2 text-sm dark:border-surface-600 dark:bg-surface-800 dark:text-surface-100">
            <option value="gpt-4o">GPT-4o</option>
            <option value="gpt-4o-mini">GPT-4o Mini</option>
            <option value="claude-3-sonnet">Claude 3 Sonnet</option>
            <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
          </select>
        </div>
      </div>
      <button onClick={() => onComplete({ name, type, model })} className="mt-6 w-full rounded-lg bg-primary-600 py-2.5 text-sm font-medium text-white hover:bg-primary-700">Create Agent</button>
    </div>
  );
}