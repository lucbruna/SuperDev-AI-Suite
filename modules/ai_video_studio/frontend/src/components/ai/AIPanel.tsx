import { useState } from 'react';
import { Sparkles } from 'lucide-react';
import { Tabs } from '@/ui';
import AssetSuggestions from './AssetSuggestions';
import ScriptWriter from './ScriptWriter';
import VoiceGenerator from './VoiceGenerator';

const TABS = [
  { id: 'script', label: 'Script' },
  { id: 'voice', label: 'Voice' },
  { id: 'assets', label: 'Assets' },
];

export default function AIPanel() {
  const [tab, setTab] = useState('script');

  return (
    <div className="flex h-full flex-col bg-panel">
      <div className="flex items-center gap-2 border-b border-border px-4 py-3">
        <Sparkles className="h-4 w-4 text-primary" />
        <span className="text-sm font-semibold text-content">AI Assistant</span>
      </div>
      <div className="border-b border-border px-3 py-2">
        <Tabs tabs={TABS} value={tab} onChange={setTab} className="w-full" />
      </div>
      <div className="min-h-0 flex-1 overflow-y-auto p-4">
        {tab === 'script' ? <ScriptWriter /> : tab === 'voice' ? <VoiceGenerator /> : <AssetSuggestions />}
      </div>
    </div>
  );
}
