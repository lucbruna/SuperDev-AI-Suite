import React, { useState, useRef, useEffect } from 'react';

interface Provider {
  id: string;
  name: string;
  healthy: boolean;
  enabled: boolean;
}

const PROVIDERS: Provider[] = [
  { id: 'openai', name: 'OpenAI', healthy: true, enabled: true },
  { id: 'anthropic', name: 'Anthropic', healthy: true, enabled: true },
  { id: 'google', name: 'Google AI', healthy: true, enabled: true },
  { id: 'deepseek', name: 'DeepSeek', healthy: false, enabled: false },
  { id: 'meta', name: 'Meta', healthy: true, enabled: false },
  { id: 'local', name: 'Local (Ollama)', healthy: true, enabled: true },
];

interface ProviderSelectorProps {
  provider: string;
  onChange: (provider: string) => void;
}

export default function ProviderSelector({ provider, onChange }: ProviderSelectorProps) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const current = PROVIDERS.find((p) => p.id === provider);

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-1.5 rounded-md px-2.5 py-1.5 text-xs text-gray-300 hover:bg-gray-800 transition-colors"
      >
        <span className={`h-1.5 w-1.5 rounded-full ${current?.healthy ? 'bg-green-500' : 'bg-red-500'}`} />
        <span>{current?.name || 'Select provider'}</span>
        <svg className={`h-3 w-3 transition-transform ${open ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {open && (
        <div className="absolute left-0 top-full z-50 mt-1 w-56 rounded-lg border border-gray-700 bg-gray-900 shadow-xl">
          <div className="p-1">
            {PROVIDERS.map((p) => (
              <div
                key={p.id}
                className="flex items-center gap-2 rounded-md px-2 py-2"
              >
                <button
                  onClick={() => {
                    onChange(p.id);
                    setOpen(false);
                  }}
                  className={`flex flex-1 items-center gap-2 text-left text-xs transition-colors ${
                    p.id === provider ? 'text-blue-300' : 'text-gray-300 hover:text-white'
                  }`}
                >
                  <span className={`h-2 w-2 rounded-full ${p.healthy ? 'bg-green-500' : 'bg-red-500'}`} />
                  <span>{p.name}</span>
                </button>
                <button
                  onClick={() => {
                    p.enabled = !p.enabled;
                  }}
                  className={`relative inline-flex h-4 w-7 items-center rounded-full transition-colors ${p.enabled ? 'bg-blue-600' : 'bg-gray-700'}`}
                >
                  <span
                    className={`inline-block h-3 w-3 transform rounded-full bg-white transition-transform ${
                      p.enabled ? 'translate-x-3.5' : 'translate-x-0.5'
                    }`}
                  />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
