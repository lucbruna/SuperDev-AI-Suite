import { useState } from 'react';
import { Loader2, Mic, Play, Plus } from 'lucide-react';
import { Badge, Button, Field, Select } from '@/ui';

interface VoiceOption {
  id: string;
  name: string;
  language: string;
  gender: string;
  emotion: string;
}

const VOICES: VoiceOption[] = [
  { id: 'marina', name: 'Marina', language: 'pt-BR', gender: 'Female', emotion: 'Friendly' },
  { id: 'daniel', name: 'Daniel', language: 'pt-BR', gender: 'Male', emotion: 'Professional' },
  { id: 'amelia', name: 'Amelia', language: 'en-US', gender: 'Female', emotion: 'Energetic' },
  { id: 'james', name: 'James', language: 'en-US', gender: 'Male', emotion: 'Calm' },
];

export default function VoiceGenerator() {
  const [voiceId, setVoiceId] = useState(VOICES[0].id);
  const [emotion, setEmotion] = useState('Friendly');
  const [speed, setSpeed] = useState('1.0');
  const [loading, setLoading] = useState(false);
  const [generated, setGenerated] = useState<string[]>([]);

  const voice = VOICES.find((item) => item.id === voiceId) ?? VOICES[0];

  const generate = () => {
    if (loading) return;
    setLoading(true);
    window.setTimeout(() => {
      setGenerated((list) => [...list, `${voice.name} • ${emotion}`]);
      setLoading(false);
    }, 800);
  };

  return (
    <div className="space-y-4">
      <Field label="Voice profile">
        <Select value={voiceId} onChange={(event) => setVoiceId(event.target.value)}>
          {VOICES.map((item) => (
            <option key={item.id} value={item.id}>
              {item.name} — {item.language} ({item.gender})
            </option>
          ))}
        </Select>
      </Field>
      <div className="grid grid-cols-2 gap-3">
        <Field label="Emotion">
          <Select value={emotion} onChange={(event) => setEmotion(event.target.value)}>
            {['Friendly', 'Professional', 'Energetic', 'Calm', 'Excited'].map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </Select>
        </Field>
        <Field label="Speed">
          <Select value={speed} onChange={(event) => setSpeed(event.target.value)}>
            {['0.75', '1.0', '1.25', '1.5'].map((item) => (
              <option key={item} value={item}>
                {item}x
              </option>
            ))}
          </Select>
        </Field>
      </div>
      <div className="flex gap-2">
        <Button variant="secondary" className="flex-1">
          <Play className="h-4 w-4" /> Preview
        </Button>
        <Button className="flex-1" disabled={loading} onClick={generate}>
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Mic className="h-4 w-4" />}
          {loading ? 'Generating…' : 'Generate'}
        </Button>
      </div>
      {generated.length > 0 ? (
        <div className="space-y-2">
          {generated.map((label, index) => (
            <div
              key={`${label}-${index}`}
              className="flex items-center justify-between gap-2 rounded-lg border border-border bg-surface px-3 py-2"
            >
              <div className="flex min-w-0 items-center gap-2">
                <Mic className="h-3.5 w-3.5 shrink-0 text-primary" />
                <span className="truncate text-xs font-medium text-content">{label}</span>
              </div>
              <div className="flex shrink-0 items-center gap-1">
                <Badge variant="neutral">{voice.language}</Badge>
                <button
                  type="button"
                  aria-label="Play voice"
                  className="flex h-6 w-6 items-center justify-center rounded text-subtle transition hover:bg-panel hover:text-content"
                >
                  <Play className="h-3.5 w-3.5 fill-current" />
                </button>
                <button
                  type="button"
                  aria-label="Add to voiceover track"
                  className="flex h-6 w-6 items-center justify-center rounded text-subtle transition hover:bg-panel hover:text-content"
                >
                  <Plus className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
}
