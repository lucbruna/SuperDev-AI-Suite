"use client";

import { useEffect, useMemo, useState } from "react";
import { videoStudioApi, type EditTimeline, type EditTimelineClip } from "@/api/videoStudio";

type Props = {
  timeline: EditTimeline;
  jobId?: string;
  editedOutputUrl?: string | null;
  title?: string;
  onSaved?: (timeline: EditTimeline) => void;
};

function formatTime(seconds: number): string {
  const safe = Math.max(0, seconds);
  const minutes = Math.floor(safe / 60);
  const remainder = safe - minutes * 60;
  return `${String(minutes).padStart(2, "0")}:${remainder.toFixed(1).padStart(4, "0")}`;
}

function reflowTimeline(timeline: EditTimeline): EditTimeline {
  let cursor = 0;
  const tracks = timeline.tracks.map((track) => {
    if (track.type !== "video") return track;
    const clips = track.clips.map((clip, index) => {
      const start = cursor;
      const end = start + clip.duration_frames;
      const next = track.clips[index + 1];
      const overlap = clip.transition_out?.type === "crossfade" && next
        ? Math.min(clip.transition_out.duration_frames, Math.floor(clip.duration_frames / 2), Math.floor(next.duration_frames / 2))
        : 0;
      cursor = end - overlap;
      return { ...clip, start_frame: start, end_frame: end, start_seconds: start / timeline.fps, end_seconds: end / timeline.fps,
        transition_out: clip.transition_out ? { ...clip.transition_out, overlap_frames: overlap } : undefined };
    });
    return { ...track, clips };
  });
  return { ...timeline, tracks, duration_frames: cursor, duration_seconds: cursor / timeline.fps };
}
function clipLabel(clip: EditTimelineClip, trackType: string): string {
  if (clip.text) return clip.text;
  if (clip.shot_type) return `Cena ${(clip.scene_index ?? 0) + 1} · ${clip.shot_type}`;
  if (clip.asset) return clip.asset.split(/[\\/]/).pop() ?? clip.asset;
  return trackType === "video" ? `Cena ${(clip.scene_index ?? 0) + 1}` : "Mídia";
}

export default function EditTimelinePanel({ timeline, jobId, editedOutputUrl, title = "Editor de timeline", onSaved }: Props) {
  const [draft, setDraft] = useState<EditTimeline>(timeline);
  const [selected, setSelected] = useState<number>(0);
  const [playheadFrame, setPlayheadFrame] = useState(0);
  const [saving, setSaving] = useState(false);
  const [rendering, setRendering] = useState(false);
  const [renderUrl, setRenderUrl] = useState(editedOutputUrl ?? "");
  const [message, setMessage] = useState("");
  const [dirty, setDirty] = useState(false);
  const [musicAsset, setMusicAsset] = useState("");
  const [musicStart, setMusicStart] = useState("0");
  const [musicEnd, setMusicEnd] = useState("10");
  const [musicVolume, setMusicVolume] = useState("0.25");
  const [musicFadeIn, setMusicFadeIn] = useState("1");
  const [musicFadeOut, setMusicFadeOut] = useState("1");
  const [sfxAsset, setSfxAsset] = useState("");
  const [sfxStart, setSfxStart] = useState("0");
  const [sfxEnd, setSfxEnd] = useState("1");
  const [sfxVolume, setSfxVolume] = useState("0.8");
  const [sfxFadeIn, setSfxFadeIn] = useState("0");
  const [sfxFadeOut, setSfxFadeOut] = useState("0.2");
  const [savingAudio, setSavingAudio] = useState(false);
  const videoTrack = draft.tracks.find((track) => track.type === "video");
  const clips = videoTrack?.clips ?? [];
  const duration = Math.max(1, draft.duration_frames);
  const selectedClip = clips[selected] ?? null;

  useEffect(() => { setDraft(timeline); setDirty(false); setSelected(0); }, [timeline]);
  useEffect(() => { setRenderUrl(editedOutputUrl ?? ""); }, [editedOutputUrl]);

  const sceneOrder = useMemo(
    () => clips.map((clip, index) => clip.source_scene_index ?? clip.scene_index ?? index),
    [clips],
  );

  function updateClip(position: number, patch: Partial<EditTimelineClip>) {
    setDirty(true);
    setDraft((current) => reflowTimeline({
      ...current,
      tracks: current.tracks.map((track) => track.type !== "video" ? track : {
        ...track,
        clips: track.clips.map((clip, index) => index === position ? { ...clip, ...patch } : clip),
      }),
    }));
  }

  function moveClip(position: number, delta: number) {
    setDirty(true);
    const target = position + delta;
    if (target < 0 || target >= clips.length) return;
    setDraft((current) => {
      const tracks = current.tracks.map((track) => {
        if (track.type !== "video") return track;
        const next = [...track.clips];
        [next[position], next[target]] = [next[target], next[position]];
        return { ...track, clips: next };
      });
      return reflowTimeline({ ...current, tracks });
    });
    setSelected(target);
  }

  async function saveDraft() {
    if (!jobId || !videoTrack) return;
    setSaving(true);
    setMessage("");
    try {
      const payload = {
        scene_order: sceneOrder,
        scene_edits: clips.map((clip, index) => ({
          scene_index: sceneOrder[index],
          duration_frames: clip.duration_frames,
          transition_type: clip.transition_out?.type ?? "cut",
          transition_duration_frames: clip.transition_out?.duration_frames ?? Math.max(2, Math.round(draft.fps * 0.5)),
        })),
      };
      const result = await videoStudioApi.updateJobTimeline(jobId, payload);
      setDraft(result.edit_timeline);
      setDirty(false);
      onSaved?.(result.edit_timeline);
      setMessage("Rascunho salvo no SQLite local. Renderize para gerar o novo MP4.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Não foi possível salvar o rascunho.");
    } finally {
      setSaving(false);
    }
  }

  async function saveAudioDraft() {
    if (!jobId || dirty || saving) return;
    const parseClip = (asset: string, start: string, end: string, volume: string, fadeIn: string, fadeOut: string) => {
      if (!asset.trim()) return null;
      const startValue = Number(start);
      const endValue = Number(end);
      const volumeValue = Number(volume);
      const fadeInValue = Number(fadeIn);
      const fadeOutValue = Number(fadeOut);
      if (![startValue, endValue, volumeValue, fadeInValue, fadeOutValue].every(Number.isFinite) ||
          startValue < 0 || endValue <= startValue || volumeValue < 0 || volumeValue > 2 ||
          fadeInValue < 0 || fadeOutValue < 0 || fadeInValue > endValue - startValue || fadeOutValue > endValue - startValue) {
        throw new Error("Confira posição, fim e volume das faixas de áudio.");
      }
      return { asset: asset.trim(), start: startValue, end: endValue, volume: volumeValue, trim_start: 0, fade_in: fadeInValue, fade_out: fadeOutValue };
    };
    setSavingAudio(true);
    setMessage("");
    try {
      const existingMusic = draft.tracks.find((track) => track.role === "music")?.clips ?? [];
      const existingSfx = draft.tracks.find((track) => track.role === "sound_effect")?.clips ?? [];
      const music = existingMusic.map((clip) => ({
        asset: clip.asset ?? "", start: clip.start_seconds ?? clip.start_frame / draft.fps,
        end: clip.end_seconds ?? clip.end_frame / draft.fps, volume: clip.volume ?? 1,
        trim_start: clip.trim_start ?? 0, fade_in: clip.fade_in ?? 0, fade_out: clip.fade_out ?? 0,
      })).filter((clip) => clip.asset);
      const sfx = existingSfx.map((clip) => ({
        asset: clip.asset ?? "", start: clip.start_seconds ?? clip.start_frame / draft.fps,
        end: clip.end_seconds ?? clip.end_frame / draft.fps, volume: clip.volume ?? 1,
        trim_start: clip.trim_start ?? 0, fade_in: clip.fade_in ?? 0, fade_out: clip.fade_out ?? 0,
      })).filter((clip) => clip.asset);
      const nextMusic = parseClip(musicAsset, musicStart, musicEnd, musicVolume, musicFadeIn, musicFadeOut);
      const nextSfx = parseClip(sfxAsset, sfxStart, sfxEnd, sfxVolume, sfxFadeIn, sfxFadeOut);
      if (nextMusic) music.push(nextMusic);
      if (nextSfx) sfx.push(nextSfx);
      const result = await videoStudioApi.updateJobAudio(jobId, { music_clips: music, sfx_clips: sfx });
      setDraft(result.edit_timeline);
      onSaved?.(result.edit_timeline);
      setMusicAsset("");
      setSfxAsset("");
      setMessage(result.message);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Não foi possível salvar as faixas de áudio.");
    } finally {
      setSavingAudio(false);
    }
  }

  async function renderEdits() {
    if (!jobId || dirty || saving) return;
    setRendering(true);
    setMessage("");
    try {
      const result = await videoStudioApi.renderJobEdits(jobId);
      setRenderUrl(result.output_url);
      setMessage(result.message);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao renderizar a edição.");
    } finally {
      setRendering(false);
    }
  }

  return (
    <section className="mb-8 rounded-xl border border-surface-200 bg-white p-4 dark:border-surface-700 dark:bg-surface-900" aria-label={title}>
      <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">{title}</h2>
          <p className="mt-1 text-xs text-surface-500">
            {draft.width}×{draft.height} · {draft.fps} FPS · {formatTime(draft.duration_seconds)} · {draft.duration_frames.toLocaleString("pt-BR")} frames
          </p>
        </div>
        <span className="rounded-full bg-surface-100 px-2.5 py-1 text-xs text-surface-600 dark:bg-surface-800 dark:text-surface-300">
          Timeline v{draft.version}
        </span>
      </div>

      <div className="mb-3 overflow-x-auto">
        <div className="min-w-[620px]">
          <div className="mb-2 flex justify-between text-[10px] tabular-nums text-surface-400">
            {Array.from({ length: 6 }, (_, i) => <span key={i}>{formatTime(draft.duration_seconds * i / 5)}</span>)}
          </div>
          <div className="space-y-2">
            {draft.tracks.map((track) => (
              <div key={track.id} className="grid grid-cols-[104px_minmax(0,1fr)] items-center gap-2">
                <div className="truncate text-xs font-medium text-surface-500" title={track.id}>
                  {track.type === "video" ? "🎬 Vídeo" : track.type === "subtitle" ? "💬 Legendas" : track.role === "narration" ? "🎙️ Narração" : track.role === "music" ? "🎵 Música" : "🔊 Efeitos"}
                </div>
                <div className="relative h-12 overflow-hidden rounded-md bg-surface-100 dark:bg-surface-800">
                  {track.clips.map((clip, index) => {
                    const left = clip.start_frame / duration * 100;
                    const width = Math.max(0.8, clip.duration_frames / duration * 100);
                    const active = track.type === "video" && selected === index;
                    const color = track.type === "video" ? "bg-violet-500/85" : track.type === "subtitle" ? "bg-amber-500/85" : track.role === "narration" ? "bg-emerald-500/85" : track.role === "music" ? "bg-sky-500/85" : "bg-pink-500/85";
                    return (
                      <button key={`${track.id}-${index}`} type="button"
                        onClick={() => track.type === "video" && setSelected(index)}
                        className={`absolute top-1 h-10 overflow-hidden rounded px-2 text-left text-[10px] font-medium text-white shadow-sm ring-offset-1 ${color} ${active ? "z-10 ring-2 ring-primary-500" : "hover:brightness-110"}`}
                        style={{ left: `${left}%`, width: `${width}%` }}
                        title={clipLabel(clip, track.type)} aria-label={`${track.type} ${clipLabel(clip, track.type)}`}>
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

      {selectedClip && (
        <div className="mb-3 rounded-lg border border-surface-200 p-3 dark:border-surface-700">
          <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
            <div>
              <strong className="text-sm">Editar cena {selected + 1}</strong>
              <p className="mt-1 text-xs text-surface-500">Selecionado: Cena {selected + 1} · {selectedClip.shot_type ?? "plano personalizado"}</p>
            </div>
            <div className="flex gap-2">
              <button type="button" onClick={() => moveClip(selected, -1)} disabled={selected === 0} className="rounded border px-2 py-1 text-xs disabled:opacity-40">↑ Mover</button>
              <button type="button" onClick={() => moveClip(selected, 1)} disabled={selected === clips.length - 1} className="rounded border px-2 py-1 text-xs disabled:opacity-40">↓ Mover</button>
            </div>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            <label className="text-xs text-surface-500">Duração (segundos)
              <input type="number" min="0.5" max="60" step="0.5"
                value={(selectedClip.duration_frames / draft.fps).toFixed(2)}
                onChange={(event) => {
                  const seconds = Number(event.target.value);
                  if (Number.isFinite(seconds) && seconds >= 0.5 && seconds <= 60) {
                    updateClip(selected, { duration_frames: Math.max(1, Math.round(seconds * draft.fps)) });
                  }
                }}
                className="mt-1 block w-full rounded border border-surface-300 bg-transparent px-2 py-1.5 text-sm dark:border-surface-600" />
            </label>
            <label className="text-xs text-surface-500">Transição de saída
              <select value={selectedClip.transition_out?.type ?? "cut"}
                onChange={(event) => updateClip(selected, { transition_out: {
                  type: event.target.value,
                  duration_frames: event.target.value === "cut" ? 0 : selectedClip.transition_out?.duration_frames || Math.max(2, Math.round(draft.fps * 0.5)),
                  overlap_frames: event.target.value === "crossfade" ? selectedClip.transition_out?.overlap_frames ?? 0 : 0,
                } })}
                className="mt-1 block w-full rounded border border-surface-300 bg-transparent px-2 py-1.5 text-sm dark:border-surface-600"
                disabled={selected === clips.length - 1}>
                <option value="cut">Corte seco</option>
                <option value="crossfade">Dissolução (crossfade)</option>
                <option value="fade_through_black">Fade pelo preto</option>
              </select>
            </label>
          </div>
        </div>
      )}

      {jobId && (
        <div className="mb-4 grid gap-3 rounded-lg border border-surface-200 p-3 dark:border-surface-700 sm:grid-cols-2">
          <div className="space-y-2">
            <strong className="text-sm">🎵 Música de fundo</strong>
            <label className="block text-xs text-surface-500">Caminho do áudio gerado
              <input value={musicAsset} onChange={(event) => setMusicAsset(event.target.value)} placeholder="modules/downloads/music/faixa.wav" className="mt-1 w-full rounded border bg-transparent px-2 py-1.5 text-xs" />
            </label>
            <div className="grid grid-cols-3 gap-2">
              <label className="text-xs text-surface-500">Início (s)<input type="number" min="0" value={musicStart} onChange={(event) => setMusicStart(event.target.value)} className="mt-1 w-full rounded border bg-transparent px-2 py-1" /></label>
              <label className="text-xs text-surface-500">Fim (s)<input type="number" min="0.1" value={musicEnd} onChange={(event) => setMusicEnd(event.target.value)} className="mt-1 w-full rounded border bg-transparent px-2 py-1" /></label>
              <label className="text-xs text-surface-500">Volume (0–2)<input type="number" min="0" max="2" step="0.05" value={musicVolume} onChange={(event) => setMusicVolume(event.target.value)} className="mt-1 w-full rounded border bg-transparent px-2 py-1" /></label>
              <label className="text-xs text-surface-500">Fade-in (s)<input type="number" min="0" step="0.1" value={musicFadeIn} onChange={(event) => setMusicFadeIn(event.target.value)} className="mt-1 w-full rounded border bg-transparent px-2 py-1" /></label>
              <label className="text-xs text-surface-500">Fade-out (s)<input type="number" min="0" step="0.1" value={musicFadeOut} onChange={(event) => setMusicFadeOut(event.target.value)} className="mt-1 w-full rounded border bg-transparent px-2 py-1" /></label>
            </div>
          </div>
          <div className="space-y-2">
            <strong className="text-sm">🔊 Efeito sonoro</strong>
            <label className="block text-xs text-surface-500">Caminho do áudio gerado
              <input value={sfxAsset} onChange={(event) => setSfxAsset(event.target.value)} placeholder="modules/downloads/effects/impact.wav" className="mt-1 w-full rounded border bg-transparent px-2 py-1.5 text-xs" />
            </label>
            <div className="grid grid-cols-3 gap-2">
              <label className="text-xs text-surface-500">Início (s)<input type="number" min="0" value={sfxStart} onChange={(event) => setSfxStart(event.target.value)} className="mt-1 w-full rounded border bg-transparent px-2 py-1" /></label>
              <label className="text-xs text-surface-500">Fim (s)<input type="number" min="0.1" value={sfxEnd} onChange={(event) => setSfxEnd(event.target.value)} className="mt-1 w-full rounded border bg-transparent px-2 py-1" /></label>
              <label className="text-xs text-surface-500">Volume (0–2)<input type="number" min="0" max="2" step="0.05" value={sfxVolume} onChange={(event) => setSfxVolume(event.target.value)} className="mt-1 w-full rounded border bg-transparent px-2 py-1" /></label>
              <label className="text-xs text-surface-500">Fade-in (s)<input type="number" min="0" step="0.1" value={sfxFadeIn} onChange={(event) => setSfxFadeIn(event.target.value)} className="mt-1 w-full rounded border bg-transparent px-2 py-1" /></label>
              <label className="text-xs text-surface-500">Fade-out (s)<input type="number" min="0" step="0.1" value={sfxFadeOut} onChange={(event) => setSfxFadeOut(event.target.value)} className="mt-1 w-full rounded border bg-transparent px-2 py-1" /></label>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2 sm:col-span-2">
            <button type="button" onClick={saveAudioDraft} disabled={savingAudio || dirty || saving || (!musicAsset.trim() && !sfxAsset.trim() && !draft.tracks.some((track) => track.role === "music" || track.role === "sound_effect"))} className="rounded-md border border-surface-300 px-3 py-2 text-xs font-semibold disabled:opacity-40 dark:border-surface-600">
              {savingAudio ? "Salvando áudio…" : "Salvar faixas de áudio"}
            </button>
            <span className="text-[11px] text-surface-400">Use arquivos nas pastas geradas music, effects, voice ou dubbing. Caminhos externos são bloqueados.</span>
          </div>
        </div>
      )}

      <div className="flex flex-wrap items-center gap-3 border-t border-surface-100 pt-3 dark:border-surface-800">
        <label className="flex min-w-[220px] flex-1 items-center gap-2 text-xs text-surface-500">
          <span>Cursor</span>
          <input aria-label="Posição do cursor da timeline" type="range" min={0} max={draft.duration_frames} step={1}
            value={Math.min(playheadFrame, draft.duration_frames)}
            onChange={(event) => setPlayheadFrame(Number(event.target.value))} className="w-full accent-primary-600" />
          <span className="w-14 text-right tabular-nums">{formatTime(playheadFrame / draft.fps)}</span>
        </label>
        {jobId && <>
          <button type="button" onClick={saveDraft} disabled={saving || !dirty} className="rounded-md border border-surface-300 px-3 py-2 text-xs font-semibold disabled:opacity-40 dark:border-surface-600">
            {saving ? "Salvando…" : "Salvar rascunho"}
          </button>
          <button type="button" onClick={renderEdits} disabled={rendering || saving || dirty} className="rounded-md bg-primary-600 px-3 py-2 text-xs font-semibold text-white disabled:opacity-40">
            {rendering ? "Renderizando MP4…" : "Renderizar edição"}
          </button>
        </>}
      </div>
      {message && <p role="status" className="mt-2 text-xs text-surface-500">{message}</p>}
      {renderUrl && <p className="mt-2 text-xs"><a className="text-primary-600 underline" href={renderUrl} target="_blank" rel="noreferrer">Abrir MP4 renderizado</a></p>}
      <p className="mt-2 text-[11px] text-surface-400">
        O rascunho fica no SQLite local. Música, efeitos e narração por cena são mixados na renderização; uma faixa única original não é reposicionada automaticamente.
      </p>
    </section>
  );
}
