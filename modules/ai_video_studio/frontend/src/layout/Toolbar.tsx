import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Check, Pause, Play, Redo2, Save, Undo2, ZoomIn, ZoomOut } from 'lucide-react';
import { formatDuration } from '@/utils';
import { Button, IconButton } from '@/ui';

export default function Toolbar() {
  const navigate = useNavigate();
  const [playing, setPlaying] = useState(false);
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    window.setTimeout(() => setSaved(false), 1500);
  };

  return (
    <div className="flex h-12 shrink-0 items-center gap-2 border-b border-border bg-panel px-3">
      <IconButton icon={Undo2} label="Undo" size="sm" />
      <IconButton icon={Redo2} label="Redo" size="sm" />
      <span className="mx-1 h-5 w-px bg-border" />
      <IconButton icon={playing ? Pause : Play} label={playing ? 'Pause' : 'Play'} size="sm" onClick={() => setPlaying((value) => !value)} />
      <span className="font-mono text-xs text-subtle">{formatDuration(12.4)}</span>
      <span className="mx-1 h-5 w-px bg-border" />
      <IconButton icon={ZoomOut} label="Zoom out" size="sm" />
      <span className="text-xs text-subtle">100%</span>
      <IconButton icon={ZoomIn} label="Zoom in" size="sm" />
      <div className="ml-auto flex items-center gap-2">
        {saved ? (
          <span className="flex items-center gap-1 text-xs text-emerald-500">
            <Check className="h-3.5 w-3.5" /> Saved
          </span>
        ) : null}
        <IconButton icon={Save} label="Save" size="sm" onClick={handleSave} />
        <Button size="sm" onClick={() => navigate('/render')}>
          Render
        </Button>
      </div>
    </div>
  );
}
