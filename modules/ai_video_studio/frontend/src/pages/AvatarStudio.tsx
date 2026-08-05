import { useState } from 'react';
import { Pencil, Plus, Trash2, UserRound } from 'lucide-react';
import { useAppStore } from '@/store';
import { Button, Card, CardBody, CardHeader, Field, IconButton, Select, SectionHeader } from '@/ui';

const FACES = ['Realistic', 'Anime', 'Cartoon', 'Stylized'];
const HAIR = ['Short', 'Long', 'Bald', 'Curly'];
const CLOTHING = ['Business', 'Casual', 'Lab coat', 'Farming gear'];
const EMOTIONS = ['Neutral', 'Smiling', 'Serious'];
const GESTURES = ['None', 'Wave', 'Point', 'Hands crossed'];

const SAVED_AVATARS = [
  { id: 'av1', name: 'Maria', face: 'Realistic', hair: 'Long', clothing: 'Business', emotion: 'Smiling', gesture: 'Wave' },
  { id: 'av2', name: 'João', face: 'Stylized', hair: 'Short', clothing: 'Farming gear', emotion: 'Neutral', gesture: 'None' },
  { id: 'av3', name: 'Sofia', face: 'Anime', hair: 'Curly', clothing: 'Casual', emotion: 'Serious', gesture: 'Point' },
];

export default function AvatarStudio() {
  const addNotification = useAppStore((state) => state.addNotification);
  const [config, setConfig] = useState({
    face: FACES[0],
    hair: HAIR[0],
    clothing: CLOTHING[0],
    emotion: EMOTIONS[0],
    gesture: GESTURES[0],
  });

  const set = (key: keyof typeof config) => (event: React.ChangeEvent<HTMLSelectElement>) =>
    setConfig((previous) => ({ ...previous, [key]: event.target.value }));

  return (
    <div>
      <SectionHeader
        title="Avatar Studio"
        subtitle="Create and manage AI presenters"
        action={
          <Button>
            <Plus className="h-4 w-4" /> Create avatar
          </Button>
        }
      />

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="self-start">
          <CardHeader title="Avatar configuration" />
          <CardBody className="space-y-4">
            <Field label="Face">
              <Select value={config.face} onChange={set('face')}>{FACES.map((option) => <option key={option}>{option}</option>)}</Select>
            </Field>
            <Field label="Hair">
              <Select value={config.hair} onChange={set('hair')}>{HAIR.map((option) => <option key={option}>{option}</option>)}</Select>
            </Field>
            <Field label="Clothing">
              <Select value={config.clothing} onChange={set('clothing')}>{CLOTHING.map((option) => <option key={option}>{option}</option>)}</Select>
            </Field>
            <Field label="Emotion">
              <Select value={config.emotion} onChange={set('emotion')}>{EMOTIONS.map((option) => <option key={option}>{option}</option>)}</Select>
            </Field>
            <Field label="Gesture">
              <Select value={config.gesture} onChange={set('gesture')}>{GESTURES.map((option) => <option key={option}>{option}</option>)}</Select>
            </Field>
          </CardBody>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader title="Preview" />
          <CardBody>
            <div className="flex flex-col items-center gap-6">
              <div className="flex h-48 w-48 items-center justify-center rounded-full bg-gradient-to-br from-primary/30 to-accent/30">
                <UserRound className="h-20 w-20 text-content" />
              </div>
              <div className="w-full max-w-md space-y-1.5 rounded-lg border border-border bg-surface p-4">
                {Object.entries(config).map(([key, value]) => (
                  <div key={key} className="flex justify-between text-sm">
                    <span className="capitalize text-subtle">{key}</span>
                    <span className="font-medium text-content">{value}</span>
                  </div>
                ))}
              </div>
              <div className="flex gap-2">
                <Button variant="ghost">Preview</Button>
                <Button
                  onClick={() =>
                    addNotification({ kind: 'success', title: 'Avatar saved', body: `${config.face} presenter added to your library.` })
                  }
                >
                  Save avatar
                </Button>
              </div>
            </div>
          </CardBody>
        </Card>
      </div>

      <section className="mt-8">
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wider text-subtle">Saved avatars</h2>
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {SAVED_AVATARS.map((avatar) => (
            <Card key={avatar.id} className="flex items-center gap-3 p-4">
              <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-primary/30 to-accent/30">
                <UserRound className="h-7 w-7 text-content" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="font-medium text-content">{avatar.name}</p>
                <p className="truncate text-xs text-subtle">
                  {avatar.face} · {avatar.clothing} · {avatar.emotion}
                </p>
              </div>
              <IconButton icon={Pencil} label="Edit" size="sm" />
              <IconButton icon={Trash2} label="Delete" size="sm" />
            </Card>
          ))}
        </div>
      </section>
    </div>
  );
}
