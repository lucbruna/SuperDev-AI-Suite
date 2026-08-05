import { Play, Sparkles, Tv } from 'lucide-react';
import { Badge } from '@/ui';
import PreviewControls from './PreviewControls';

export default function PreviewCanvas() {
  return (
    <div className="flex h-full min-h-0 flex-col">
      <div className="relative flex min-h-0 flex-1 items-center justify-center overflow-hidden rounded-xl border border-border bg-black">
        <div className="relative aspect-video w-full max-w-4xl overflow-hidden rounded-lg">
          <div className="absolute inset-0 bg-gradient-to-br from-indigo-600 via-primary to-cyan-500" />
          <div className="absolute -left-16 -top-16 h-64 w-64 rounded-full bg-white/10 blur-2xl" />
          <div className="absolute -bottom-20 -right-12 h-72 w-72 rounded-full bg-cyan-300/20 blur-2xl" />
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 p-8 text-center">
            <span className="rounded-full bg-white/15 px-3 py-1 text-xs font-medium text-white backdrop-blur">
              Product Launch 2026
            </span>
            <h2 className="max-w-md text-3xl font-bold leading-tight text-white drop-shadow">
              Introducing the future of farming
            </h2>
            <p className="text-sm text-white/80">Short-form highlight for social channels</p>
            <div className="mt-3 flex items-center gap-3 rounded-lg bg-black/40 px-4 py-2.5 backdrop-blur">
              <span className="flex h-9 w-9 items-center justify-center rounded-full bg-white/20">
                <Tv className="h-4 w-4 text-white" />
              </span>
              <div className="text-left">
                <p className="text-xs font-semibold text-white">AI Presenter</p>
                <p className="text-[10px] text-white/60">16:9 • 30 fps • 1080p</p>
              </div>
            </div>
          </div>
          <div className="absolute left-3 top-3 flex items-center gap-2">
            <Badge variant="info">
              <Sparkles className="h-3 w-3" /> AI Scene
            </Badge>
            <Badge variant="neutral">1080p</Badge>
          </div>
          <button
            type="button"
            aria-label="Play preview"
            className="absolute inset-0 m-auto flex h-16 w-16 items-center justify-center rounded-full bg-white/90 text-black shadow-xl transition hover:scale-105 hover:bg-white"
          >
            <Play className="h-7 w-7 translate-x-0.5 fill-current" />
          </button>
        </div>
      </div>
      <PreviewControls className="mt-3 shrink-0" />
    </div>
  );
}
