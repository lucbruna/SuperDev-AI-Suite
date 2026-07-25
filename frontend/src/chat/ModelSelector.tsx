import React, { useState, useRef, useEffect } from 'react';

interface Model {
  id: string;
  name: string;
  provider: string;
  contextWindow: number;
  cost: { input: number; output: number };
  recentlyUsed?: boolean;
}

const MODELS: Model[] = [
  { id: 'gpt-4o', name: 'GPT-4o', provider: 'OpenAI', contextWindow: 128000, cost: { input: 2.5, output: 10 } },
  { id: 'gpt-4o-mini', name: 'GPT-4o Mini', provider: 'OpenAI', contextWindow: 128000, cost: { input: 0.15, output: 0.6 } },
  { id: 'claude-3-opus', name: 'Claude 3 Opus', provider: 'Anthropic', contextWindow: 200000, cost: { input: 15, output: 75 } },
  { id: 'claude-3-sonnet', name: 'Claude 3.5 Sonnet', provider: 'Anthropic', contextWindow: 200000, cost: { input: 3, output: 15 } },
  { id: 'claude-3-haiku', name: 'Claude 3 Haiku', provider: 'Anthropic', contextWindow: 200000, cost: { input: 0.25, output: 1.25 } },
  { id: 'gemini-1.5-pro', name: 'Gemini 1.5 Pro', provider: 'Google', contextWindow: 1000000, cost: { input: 1.25, output: 5 } },
  { id: 'gemini-1.5-flash', name: 'Gemini 1.5 Flash', provider: 'Google', contextWindow: 1000000, cost: { input: 0.075, output: 0.3 } },
  { id: 'deepseek-coder', name: 'DeepSeek Coder', provider: 'DeepSeek', contextWindow: 128000, cost: { input: 0.14, output: 0.28 } },
  { id: 'llama-3.1-70b', name: 'Llama 3.1 70B', provider: 'Meta', contextWindow: 131072, cost: { input: 0.59, output: 0.79 } },
];

interface ModelSelectorProps {
  model: string;
  onChange: (model: string) => void;
}

export default function ModelSelector({ model, onChange }: ModelSelectorProps) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const grouped = MODELS.reduce<Record<string, Model[]>>((acc, m) => {
    (acc[m.provider] = acc[m.provider] || []).push(m);
    return acc;
  }, {});

  const current = MODELS.find((m) => m.id === model);

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-1.5 rounded-md px-2.5 py-1.5 text-xs text-gray-300 hover:bg-gray-800 transition-colors"
      >
        <span>{current?.name || 'Select model'}</span>
        <svg className={`h-3 w-3 transition-transform ${open ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {open && (
        <div className="absolute left-0 top-full z-50 mt-1 w-72 rounded-lg border border-gray-700 bg-gray-900 shadow-xl">
          <div className="max-h-80 overflow-y-auto p-1">
            {Object.entries(grouped).map(([provider, models]) => (
              <div key={provider}>
                <div className="px-2 py-1.5 text-[10px] font-semibold uppercase tracking-wider text-gray-500">
                  {provider}
                </div>
                {models.map((m) => (
                  <button
                    key={m.id}
                    onClick={() => {
                      onChange(m.id);
                      setOpen(false);
                    }}
                    className={`flex w-full items-center justify-between rounded-md px-2 py-2 text-left text-xs transition-colors ${
                      m.id === model
                        ? 'bg-blue-600/20 text-blue-300'
                        : 'text-gray-300 hover:bg-gray-800'
                    }`}
                  >
                    <div>
                      <div className="font-medium">{m.name}</div>
                      <div className="text-[10px] text-gray-500">
                        {m.contextWindow.toLocaleString()} ctx · ${m.cost.input}/{m.cost.output} per 1M tokens
                      </div>
                    </div>
                    {m.recentlyUsed && (
                      <span className="text-[10px] text-green-400">Recent</span>
                    )}
                  </button>
                ))}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
