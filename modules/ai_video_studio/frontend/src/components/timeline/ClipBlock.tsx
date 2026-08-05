import { GripVertical } from 'lucide-react';
import { cn } from '@/utils';
import type { TimelineClip } from './Timeline';

export default function ClipBlock({ clip, pxPerSecond }: { clip: TimelineClip; pxPerSecond: number }) {
  return (
    <div
      className={cn('absolute inset-y-1.5 flex items-center gap-1 overflow-hidden rounded-md px-2 text-white', clip.color)}
      style={{ left: clip.start * pxPerSecond, width: clip.duration * pxPerSecond }}
      title={clip.name}
    >
      <GripVertical className="h-3 w-3 shrink-0 text-white/70" />
      <span className="truncate text-[11px] font-medium">{clip.name}</span>
    </div>
  );
}
