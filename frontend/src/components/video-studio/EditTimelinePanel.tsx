"use client";

import { useMemo, useState } from "react";
import type { EditTimeline, EditTimelineClip } from "@/api/videoStudio";

type Props = {
  timeline: EditTimeline;
  title?: string;
};

function formatTime(seconds: number): string {
  const safe = Math.max(0, seconds);
  const minutes = Math.floor(safe / 60);
  const remainder = safe - minutes * 60;
  return `${String(minutes).padStart(2, "0")}:${remainder.toFixed(1).padStart(4, "0")}`;
}

function clipLabel(clip: EditTimelineClip, trackType: string): string {
  if (clip.text) return clip.text;
  if (clip.shot_type) return `Cena ${(clip.scene_index ?? 0) + 1} · ${clip.shot_type}`;
  if (clip.asset) return clip.asset.split(/[\\/]/).pop() ?? clip.asset;
  return trackType === "video" ? `Cena ${(clip.scene_index ?? 0) + 1}` : "Mídia";
}

export default function EditTimelinePanel({ timeline, title = "Editor de timeline" }: Props) {
  const [selected, setSelected] = useState<{ trackId: string; clipIndex: number } | null>(null);
  const [playheadFrame, setPlayheadFrame] = useState(0);
  const duration = Math.max(1, timeline.duration_frames);
  const selectedClip = useMemo(() => {
    if (!selected) return null;
    const track = timeline.tracks.find((item) => item.id === selected.trackId);
    return track?.clips[selected.clipIndex] ?? null;
  }, [selected, timeline]);

  return (
    <section className="mb-8 rounded-xl border border-surface-200 bg-white p-4 dark:border-surface-700 dark:bg-surface-900" aria-label={title}>
      <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">{title}</h2>
          <p className="mt-1 text-xs text-surface-500">
            {timeline.width}×{timeline.height} · {timeline.fps} FPS · {formatTime(timeline.duration_seconds)} · {timeline.duration_frames.toLocaleString("pt-BR")} frames
          </p>
        </div>
        <span className="rounded-full bg-surface-100 px-2.5 py-1 text-xs text-surface-600 dark:bg-surface-800 dark:text-surface-300">
          Timeline v{timeline.version}
        </span>
      </div>

      <div className="mb-3 overflow-x-auto">
        <div className="min-w-[620px]">
          <div className="mb-2 flex justify-between text-[10px] tabular-nums text-surface-400">
            {Array.from({ length: 6 }, (_, i) => {
              const seconds = timeline.duration_seconds * i / 5;
              return <span key={i}>{formatTime(seconds)}</span>;
            })}
          </div>
          <div className="space-y-2">
            {timeline.tracks.map((track) => (
              <div key={track.id} className="grid grid-cols-[104px_minmax(0,1fr)] items-center gap-2">
                <div className="truncate text-xs font-medium text-surface-500" title={track.id}>
                  {track.type === "video" ? "🎬 Vídeo" : track.type === "subtitle" ? "💬 Legendas" : track.role === "narration" ? "🎙️ Narração" : track.role === "music" ? "🎵 Música" : "🔊 Efeitos"}
                </div>
                <div className="relative h-12 overflow-hidden rounded-md bg-surface-100 dark:bg-surface-800" style={{ backgroundImage: "linear-gradient(to right, transparent calc(20% - 1px), rgba(148,163,184,.22) 20%, transparent calc(20% + 1px))", backgroundSize: "25% 100%" }}>
                  {track.clips.map((clip, index) => {
                    const left = clip.start_frame / duration * 100;
                    const width = Math.max(0.8, clip.duration_frames / duration * 100);
                    const active = selected?.trackId === track.id && selected.clipIndex === index;
                    const color = track.type === "video" ? "bg-violet-500/85" : track.type === "subtitle" ? "bg-amber-500/85" : track.role === "narration" ? "bg-emerald-500/85" : track.role === "music" ? "bg-sky-500/85" : "bg-pink-500/85";
                    return (
                      <button
                        key={`${track.id}-${index}`}
                        type="button"
                        onClick={() => setSelected({ trackId: track.id, clipIndex: index })}
                        className={`absolute top-1 h-10 overflow-hidden rounded px-2 text-left text-[10px] font-medium text-white shadow-sm ring-offset-1 transition ${color} ${active ? "z-10 ring-2 ring-primary-500" : "hover:brightness-110"}`}
                        style={{ left: `${left}%`, width: `${width}%` }}
                        title={clipLabel(clip, track.type)}
                        aria-label={`${track.type} ${clipLabel(clip, track.type)}`}
                      >
                        <span className="block truncate">{clipLabel(clip, track.type)}</span>
                      </button>
                    );
                  })}
                  <div className="pointer-events-none absolute inset-y-0 z-20 w-px bg-red-500" style={{ left: `${playheadFrame / duration * 100}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-3 border-t border-surface-100 pt-3 dark:border-surface-800">
        <label className="flex min-w-[220px] flex-1 items-center gap-2 text-xs text-surface-500">
          <span>Cursor</span>
          <input
            aria-label="Posição do cursor da timeline"
            type="range"
            min={0}
            max={timeline.duration_frames}
            step={1}
            value={playheadFrame}
            onChange={(event) => setPlayheadFrame(Number(event.target.value))}
            className="w-full accent-primary-600"
          />
          <span className="w-14 text-right tabular-nums">{formatTime(playheadFrame / timeline.fps)}</span>
        </label>
        {selectedClip ? (
          <p className="text-xs text-surface-600 dark:text-surface-300">
            Selecionado: <strong>{clipLabel(selectedClip, "clip")}</strong> · {formatTime(selectedClip.start_frame / timeline.fps)}–{formatTime(selectedClip.end_frame / timeline.fps)}
          </p>
        ) : (
          <p className="text-xs text-surface-400">Selecione um bloco para ver seus detalhes.</p>
        )}
      </div>
      <p className="mt-2 text-[11px] text-surface-400">
        Visualização da edição gerada. Alterações destrutivas e re-renderização ainda não estão habilitadas nesta versão.
      </p>
    </section>
  );
}
