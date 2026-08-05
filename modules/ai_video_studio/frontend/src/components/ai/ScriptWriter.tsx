import { useState } from 'react';
import { Loader2, Sparkles } from 'lucide-react';
import { Button, Field, Select, Textarea } from '@/ui';

interface ScriptSection {
  time: string;
  title: string;
  narration: string;
}

const MOCK_SCRIPT: ScriptSection[] = [
  { time: '00:00', title: 'Hook', narration: 'Meet the irrigation system that thinks for itself.' },
  { time: '00:06', title: 'Problem', narration: 'Manual watering wastes time, water and yield.' },
  { time: '00:12', title: 'Solution', narration: 'Smart sensors read the soil and adjust in real time.' },
  { time: '00:20', title: 'CTA', narration: 'See the future of farming at launch.farm' },
];

export default function ScriptWriter() {
  const [prompt, setPrompt] = useState('');
  const [tone, setTone] = useState('professional');
  const [length, setLength] = useState('30');
  const [loading, setLoading] = useState(false);
  const [sections, setSections] = useState<ScriptSection[]>([]);

  const generate = () => {
    if (!prompt.trim() || loading) return;
    setLoading(true);
    window.setTimeout(() => {
      setSections(MOCK_SCRIPT);
      setLoading(false);
    }, 900);
  };

  return (
    <div className="space-y-4">
      <Field label="What should the video say?" hint="Describe the message, audience and goal.">
        <Textarea
          value={prompt}
          onChange={(event) => setPrompt(event.target.value)}
          placeholder="e.g. Launch video for a smart irrigation system, aimed at small farmers…"
        />
      </Field>
      <div className="grid grid-cols-2 gap-3">
        <Field label="Tone">
          <Select value={tone} onChange={(event) => setTone(event.target.value)}>
            <option value="professional">Professional</option>
            <option value="casual">Casual</option>
            <option value="energetic">Energetic</option>
            <option value="inspirational">Inspirational</option>
          </Select>
        </Field>
        <Field label="Length">
          <Select value={length} onChange={(event) => setLength(event.target.value)}>
            <option value="30">30 seconds</option>
            <option value="60">60 seconds</option>
            <option value="90">90 seconds</option>
          </Select>
        </Field>
      </div>
      <Button className="w-full" disabled={!prompt.trim() || loading} onClick={generate}>
        {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
        {loading ? 'Writing script…' : 'Generate script'}
      </Button>
      {sections.length > 0 ? (
        <div className="space-y-2">
          {sections.map((section) => (
            <div key={section.time} className="rounded-lg border border-border bg-surface p-3">
              <div className="flex items-center justify-between gap-2">
                <span className="text-xs font-semibold text-content">{section.title}</span>
                <span className="rounded bg-primary/10 px-1.5 py-0.5 text-[10px] tabular-nums text-primary">
                  {section.time}
                </span>
              </div>
              <p className="mt-1 text-xs leading-relaxed text-subtle">{section.narration}</p>
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
}
