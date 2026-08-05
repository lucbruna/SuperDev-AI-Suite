import { useEffect, useState } from 'react';
import { Check, Pause, Play, Upload, UploadCloud } from 'lucide-react';
import type { VoiceProfile } from '@/types';
import { fetchVoiceProfiles } from '@/api';
import { useAppStore } from '@/store';
import { cn } from '@/utils';
import { Avatar, Badge, Button, Card, CardBody, CardHeader, IconButton, SectionHeader } from '@/ui';

const genderVariant: Record<VoiceProfile['gender'], 'info' | 'accent' | 'neutral'> = {
  male: 'info',
  female: 'accent',
  neutral: 'neutral',
};

export default function VoiceStudio() {
  const addNotification = useAppStore((state) => state.addNotification);
  const [voices, setVoices] = useState<VoiceProfile[]>([]);
  const [playingId, setPlayingId] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [cloning, setCloning] = useState(false);
  const [speed, setSpeed] = useState(1);
  const [pitch, setPitch] = useState(1);

  useEffect(() => {
    fetchVoiceProfiles().then(setVoices);
  }, []);

  return (
    <div>
      <SectionHeader
        title="Voice Studio"
        subtitle="Synthetic voices for narration and characters"
        action={
          <Button>
            <Upload className="h-4 w-4" /> New voice
          </Button>
        }
      />

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-4 lg:col-span-2">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-subtle">Voice profiles</h2>
          {voices.map((voice) => {
            const playing = playingId === voice.id;
            return (
              <Card key={voice.id} className="flex items-center gap-4 p-4">
                <IconButton
                  icon={playing ? Pause : Play}
                  label={playing ? 'Pause' : 'Play'}
                  onClick={() => setPlayingId(playing ? null : voice.id)}
                />
                <div className="flex h-8 items-end gap-0.5">
                  {[8, 14, 10, 18, 12, 16].map((height, index) => (
                    <span
                      key={index}
                      className={cn('w-1 rounded-full bg-accent transition-all', playing ? 'animate-pulse' : 'opacity-30')}
                      style={{ height }}
                    />
                  ))}
                </div>
                <Avatar name={voice.name} size="lg" />
                <div className="min-w-0 flex-1">
                  <p className="font-medium text-content">{voice.name}</p>
                  <p className="text-xs text-subtle">{voice.language}</p>
                </div>
                <Badge variant={genderVariant[voice.gender]}>{voice.gender}</Badge>
                <span className="text-xs text-subtle">{voice.emotion}</span>
              </Card>
            );
          })}
        </div>

        <div className="space-y-4">
          <Card>
            <CardHeader title="Clone a voice" subtitle="Upload a 10s–5min reference sample" />
            <CardBody>
              <button
                type="button"
                onClick={() => setFileName('reference_sample.wav')}
                className="flex w-full flex-col items-center gap-2 rounded-lg border-2 border-dashed border-border p-6 text-subtle transition-colors hover:border-primary/50 hover:text-content"
              >
                <UploadCloud className="h-8 w-8" />
                <span className="text-sm">{fileName ?? 'Drop a sample audio or click to browse'}</span>
              </button>
              <Button
                className="mt-4 w-full"
                variant="secondary"
                onClick={() => {
                  setCloning(true);
                  addNotification({ kind: 'info', title: 'Cloning started', body: 'Your voice clone is being trained.' });
                }}
                disabled={cloning}
              >
                {cloning ? <Check className="h-4 w-4" /> : null}
                {cloning ? 'Cloning…' : 'Start cloning'}
              </Button>
            </CardBody>
          </Card>

          <Card>
            <CardHeader title="Voice settings" />
            <CardBody className="space-y-5">
              <div>
                <div className="mb-1.5 flex justify-between text-sm">
                  <span className="text-content">Speed</span>
                  <span className="font-medium text-subtle">{speed.toFixed(1)}×</span>
                </div>
                <input type="range" min={0.5} max={2} step={0.1} value={speed} onChange={(event) => setSpeed(Number(event.target.value))} className="w-full accent-[var(--color-primary)]" />
              </div>
              <div>
                <div className="mb-1.5 flex justify-between text-sm">
                  <span className="text-content">Pitch</span>
                  <span className="font-medium text-subtle">{pitch.toFixed(1)}×</span>
                </div>
                <input type="range" min={0.5} max={2} step={0.1} value={pitch} onChange={(event) => setPitch(Number(event.target.value))} className="w-full accent-[var(--color-primary)]" />
              </div>
              <Button
                className="w-full"
                onClick={() => addNotification({ kind: 'success', title: 'Settings saved', body: 'Voice defaults updated.' })}
              >
                Save settings
              </Button>
            </CardBody>
          </Card>
        </div>
      </div>
    </div>
  );
}
