"use client";

import { useState } from "react";

const PROVIDERS = [
  { id: "openai", name: "OpenAI", models: ["gpt-4o", "gpt-4o-mini", "o1", "o1-mini"], icon: "🔵", default: true },
  { id: "anthropic", name: "Anthropic", models: ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"], icon: "🟣", default: false },
  { id: "gemini", name: "Google Gemini", models: ["gemini-1.5-pro", "gemini-1.5-flash"], icon: "🟢", default: false },
  { id: "ollama", name: "Ollama (Local)", models: ["llama3", "mistral", "codellama"], icon: "🟠", default: false },
];

interface ProviderSetupProps {
  onComplete: (providers: Record<string, string>) => void;
}

export function ProviderSetup({ onComplete }: ProviderSetupProps) {
  const [selected, setSelected] = useState<Record<string, string>>({ "openai": "gpt-4o" });
  const [showApiKey, setShowApiKey] = useState<Record<string, string>>({});

  const toggleProvider = (id: string) => {
    if (selected[id]) {
      const next = { ...selected };
      delete next[id];
      setSelected(next);
    } else {
      setSelected({ ...selected, [id]: PROVIDERS.find((p) => p.id === id)?.models[0] || "" });
    }
  };

  const setModel = (id: string, model: string) => setSelected({ ...selected, [id]: model });

  const setKey = (id: string, key: string) => setShowApiKey({ ...showApiKey, [id]: key });

  return (
    <div>
      <h3 className="text-lg font-bold text-surface-900 dark:text-surface-50">Configure AI Providers</h3>
      <p className="mt-1 text-sm text-surface-600 dark:text-surface-400">Connect your AI providers to enable agent intelligence</p>
      <div className="mt-4 space-y-3">
        {PROVIDERS.map((p) => (
          <div key={p.id} className="rounded-xl border bg-white p-4 dark:border-surface-700 dark:bg-surface-900">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-xl">{p.icon}</span>
                <span className="font-semibold text-surface-900 dark:text-surface-50">{p.name}</span>
              </div>
              <button onClick={() => toggleProvider(p.id)} className={`rounded-lg px-3 py-1 text-xs font-medium ${selected[p.id] ? "bg-primary-600 text-white" : "bg-surface-200 text-surface-600"}`}>
                {selected[p.id] ? "Connected" : "Connect"}
              </button>
            </div>
            {selected[p.id] && (
              <div className="mt-3 space-y-2">
                <select value={selected[p.id]} onChange={(e) => setModel(p.id, e.target.value)} className="w-full rounded-lg border border-surface-300 bg-white px-3 py-1.5 text-sm dark:border-surface-600 dark:bg-surface-800">
                  {p.models.map((m) => <option key={m} value={m}>{m}</option>)}
                </select>
                <input type="password" value={showApiKey[p.id] || ""} onChange={(e) => setKey(p.id, e.target.value)} placeholder="API Key (optional)" className="w-full rounded-lg border border-surface-300 bg-white px-3 py-1.5 text-sm dark:border-surface-600 dark:bg-surface-800" />
              </div>
            )}
          </div>
        ))}
      </div>
      <button onClick={() => onComplete(selected)} className="mt-4 w-full rounded-lg bg-primary-600 py-2.5 text-sm font-medium text-white hover:bg-primary-700">Continue</button>
    </div>
  );
}