import { Users } from 'lucide-react';
import { Avatar, Button } from '@/ui';
import PreviewCanvas from '@/components/preview/PreviewCanvas';
import AIPanel from '@/components/ai/AIPanel';
import Timeline from '@/components/timeline/Timeline';

export default function Editor() {
  return (
    <div className="flex h-full flex-col bg-surface">
      <div className="flex h-12 shrink-0 items-center justify-between border-b border-border bg-panel px-4">
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold text-content">Product Launch 2026</span>
          <span className="flex items-center gap-1 text-xs text-emerald-500">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
            Saved
          </span>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex -space-x-1">
            <Avatar name="Ana Souza" size="sm" />
            <Avatar name="Bruno Lima" size="sm" />
            <Avatar name="Carla Mendes" size="sm" />
          </div>
          <Button size="sm" variant="secondary">
            <Users className="h-4 w-4" /> Share
          </Button>
        </div>
      </div>
      <div className="flex min-h-0 flex-1">
        <div className="min-w-0 flex-1 overflow-y-auto p-6">
          <PreviewCanvas />
        </div>
        <div className="w-80 shrink-0 border-l border-border">
          <AIPanel />
        </div>
      </div>
      <div className="h-64 shrink-0 border-t border-border">
        <Timeline />
      </div>
    </div>
  );
}
