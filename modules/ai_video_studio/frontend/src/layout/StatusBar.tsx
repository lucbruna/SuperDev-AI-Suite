export default function StatusBar() {
  return (
    <div className="flex h-8 shrink-0 items-center gap-6 border-t border-border bg-panel px-4 text-xs text-subtle">
      <span className="truncate text-content">Product Launch 2026</span>
      <span className="hidden sm:inline">FPS 30</span>
      <span className="hidden sm:inline">Zoom 100%</span>
      <span className="flex items-center gap-1.5">
        <span className="h-2 w-2 rounded-full bg-emerald-500" />
        Idle
      </span>
      <span className="ml-auto font-mono">00:12 / 01:30</span>
    </div>
  );
}
