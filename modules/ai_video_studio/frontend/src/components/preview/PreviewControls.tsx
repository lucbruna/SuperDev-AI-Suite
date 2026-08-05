import { Maximize, Play, Settings2, SkipBack, SkipForward, Volume2 } from 'lucide-react';
import { IconButton } from '@/ui';
import { cn } from '@/utils';

export default function PreviewControls({ className }: { className?: string }) {
  return (
    <div className={cn('flex items-center gap-2 rounded-xl border border-border bg-panel px-3 py-2', className)}>
      <IconButton size="sm" icon={SkipBack} label="Back 10 seconds" />
      <button
        type="button"
        aria-label="Play"
        className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-white transition hover:bg-primary/90"
      >
        <Play className="h-4 w-4 fill-current" />
      </button>
      <IconButton size="sm" icon={SkipForward} label="Forward 10 seconds" />
      <span className="ml-1 text-xs tabular-nums text-subtle">00:12 / 00:32</span>
      <div className="ml-auto flex items-center gap-2">
        <Volume2 className="h-4 w-4 text-subtle" />
        <div className="h-1 w-20 overflow-hidden rounded-full bg-border">
          <div className="h-full w-3/4 rounded-full bg-primary" />
        </div>
        <IconButton size="sm" icon={Settings2} label="Playback settings" />
        <IconButton size="sm" icon={Maximize} label="Fullscreen" />
      </div>
    </div>
  );
}
