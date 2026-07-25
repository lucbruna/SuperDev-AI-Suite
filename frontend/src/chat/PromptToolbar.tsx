import React, { useState } from 'react';
import ModelSelector from './ModelSelector';
import ProviderSelector from './ProviderSelector';

interface PromptToolbarProps {
  model: string;
  provider: string;
  onModelChange: (model: string) => void;
  onProviderChange: (provider: string) => void;
  onTemperatureChange: (temp: number) => void;
  onMaxTokensChange: (tokens: number) => void;
  onClearChat: () => void;
}

export default function PromptToolbar({
  model,
  provider,
  onModelChange,
  onProviderChange,
  onTemperatureChange,
  onMaxTokensChange,
  onClearChat,
}: PromptToolbarProps) {
  const [temperature, setTemperature] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(2048);

  const handleTemp = (val: number) => {
    setTemperature(val);
    onTemperatureChange(val);
  };

  const handleTokens = (val: number) => {
    setMaxTokens(val);
    onMaxTokensChange(val);
  };

  return (
    <div className="flex items-center gap-3 border-b border-gray-800 bg-gray-950 px-4 py-2">
      <ModelSelector model={model} onChange={onModelChange} />
      <ProviderSelector provider={provider} onChange={onProviderChange} />

      <div className="h-5 w-px bg-gray-800" />

      <div className="flex items-center gap-2">
        <label className="text-[11px] font-medium text-gray-500">Temp</label>
        <input
          type="range"
          min="0"
          max="2"
          step="0.1"
          value={temperature}
          onChange={(e) => handleTemp(parseFloat(e.target.value))}
          className="w-16 h-1 accent-blue-500"
        />
        <span className="text-[11px] text-gray-400 w-6">{temperature.toFixed(1)}</span>
      </div>

      <div className="h-5 w-px bg-gray-800" />

      <div className="flex items-center gap-2">
        <label className="text-[11px] font-medium text-gray-500">Tokens</label>
        <input
          type="range"
          min="256"
          max="8192"
          step="256"
          value={maxTokens}
          onChange={(e) => handleTokens(parseInt(e.target.value))}
          className="w-20 h-1 accent-blue-500"
        />
        <span className="text-[11px] text-gray-400 w-10">{maxTokens}</span>
      </div>

      <div className="ml-auto">
        <button
          onClick={onClearChat}
          className="flex items-center gap-1 rounded-md px-2 py-1 text-xs text-gray-500 hover:bg-gray-800 hover:text-gray-300 transition-colors"
          title="Clear chat"
        >
          <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
          Clear
        </button>
      </div>
    </div>
  );
}
