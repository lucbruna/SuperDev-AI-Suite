import { useState } from 'react';
import { Check, Image, Music, RefreshCw, Video } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import { Badge, Button } from '@/ui';
import { cn } from '@/utils';

interface Suggestion {
  id: string;
  name: string;
  type: 'video' | 'image' | 'music';
  tag: string;
}

const SUGGESTIONS: Suggestion[] = [
  { id: 's1', name: 'Drone field footage', type: 'video', tag: 'Video' },
  { id: 's2', name: 'Sunrise irrigation shot', type: 'image', tag: 'Image' },
  { id: 's3', name: 'Upbeat acoustic bed', type: 'music', tag: 'Music' },
  { id: 's4', name: 'Farmer close-up', type: 'image', tag: 'Image' },
];

const TYPE_ICONS: Record<Suggestion['type'], LucideIcon> = {
  video: Video,
  image: Image,
  music: Music,
};

export default function AssetSuggestions() {
  const [added, setAdded] = useState<string[]>([]);
  const [regenerating, setRegenerating] = useState(false);

  const toggle = (id: string) => {
    setAdded((list) => (list.includes(id) ? list.filter((item) => item !== id) : [...list, id]));
  };

  const regenerate = () => {
    setRegenerating(true);
    window.setTimeout(() => setRegenerating(false), 700);
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between gap-2">
        <p className="text-xs text-subtle">Suggested based on your script</p>
        <Button variant="ghost" size="sm" disabled={regenerating} onClick={regenerate}>
          <RefreshCw className={cn('h-3.5 w-3.5', regenerating && 'animate-spin')} /> Refresh
        </Button>
      </div>
      <div className="grid grid-cols-2 gap-2">
        {SUGGESTIONS.map((item) => {
          const Icon = TYPE_ICONS[item.type];
          const isAdded = added.includes(item.id);
          return (
            <div key={item.id} className="flex flex-col gap-2 rounded-lg border border-border bg-surface p-3">
              <div className="flex h-16 items-center justify-center rounded-md bg-panel">
                <Icon className="h-6 w-6 text-subtle" />
              </div>
              <div>
                <p className="truncate text-xs font-medium text-content">{item.name}</p>
                <div className="mt-1">
                  <Badge variant="neutral">{item.tag}</Badge>
                </div>
              </div>
              <Button size="sm" variant={isAdded ? 'outline' : 'secondary'} onClick={() => toggle(item.id)}>
                {isAdded ? <Check className="h-3.5 w-3.5" /> : null}
                {isAdded ? 'Added' : 'Add'}
              </Button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
