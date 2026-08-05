import { ZoomIn, ZoomOut } from 'lucide-react';
import { IconButton } from '@/ui';

const round2 = (value: number) => Math.round(value * 100) / 100;

export default function ZoomControls({ zoom, onChange }: { zoom: number; onChange: (zoom: number) => void }) {
  return (
    <div className="flex items-center gap-1">
      <IconButton size="sm" icon={ZoomOut} label="Zoom out" disabled={zoom <= 0.5} onClick={() => onChange(round2(zoom - 0.25))} />
      <span className="w-10 text-center text-xs tabular-nums text-subtle">{Math.round(zoom * 100)}%</span>
      <IconButton size="sm" icon={ZoomIn} label="Zoom in" disabled={zoom >= 4} onClick={() => onChange(round2(zoom + 0.25))} />
    </div>
  );
}
