import { Film, Music, Type } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import type { TimelineTrack } from './Timeline';

const TRACK_ICONS: Record<TimelineTrack['type'], LucideIcon> = {
  video: Film,
  audio: Music,
  text: Type,
};

export default function TrackList({ tracks }: { tracks: TimelineTrack[] }) {
  return (
    <div className="w-36 shrink-0 border-r border-border bg-surface">
      <div className="flex h-6 items-center border-b border-border px-2.5 text-[10px] font-semibold uppercase tracking-wider text-subtle">
        Tracks
      </div>
      {tracks.map((track) => {
        const Icon = TRACK_ICONS[track.type];
        return (
          <div key={track.id} className="flex h-12 items-center gap-2 border-b border-border/50 px-2.5">
            <Icon className="h-3.5 w-3.5 shrink-0 text-subtle" />
            <span className="truncate text-xs font-medium text-content">{track.name}</span>
          </div>
        );
      })}
    </div>
  );
}
