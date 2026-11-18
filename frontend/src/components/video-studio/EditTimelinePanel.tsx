"use client";

import { useEffect, useMemo, useState } from "react";
import { videoStudioApi, type EditTimeline, type EditTimelineClip, type StudioAudioAsset } from "@/api/videoStudio";

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
  const [audioAssets, setAudioAssets] = useState<StudioAudioAsset[]>([]);
  const [musicAsset, setMusicAsset] = useState("");
  const [musicStart, setMusicStart] = useState("0");
  const [musicEnd, setMusicEnd] = useState("10");
  const [musicVolume, setMusicVolume] = useState("0.25");
  const [musicPan, setMusicPan] = useState("0");
  const [musicFadeIn, setMusicFadeIn] = useState("1");
  const [musicFadeOut, setMusicFadeOut] = useState("1");
  const [musicLoop, setMusicLoop] = useState(false);
  const [sfxAsset, setSfxAsset] = useState("");
  const [sfxStart, setSfxStart] = useState("0");
  const [sfxEnd, setSfxEnd] = useState("1");
  const [sfxVolume, setSfxVolume] = useState("0.8");
  const [sfxPan, setSfxPan] = useState("0");
  const [sfxFadeIn, setSfxFadeIn] = useState("0");
  const [sfxFadeOut, setSfxFadeOut] = useState("0.2");
  const [savingAudio, setSavingAudio] = useState(false);
  const [audioDirty, setAudioDirty] = useState(false);  const [audioAnalysis, setAudioAnalysis] = useState<Awaited<ReturnType<typeof videoStudioApi.analyzeJobAudio>> | null>(null);
  const [analyzingAudio, setAnalyzingAudio] = useState(false);
  const [avSyncReport, setAvSyncReport] = useState<Awaited<ReturnType<typeof videoStudioApi.analyzeJobAvSync>> | null>(null);
  const [analyzingAvSync, setAnalyzingAvSync] = useState(false);
  const [renderQuality, setRenderQuality] = useState<Awaited<ReturnType<typeof videoStudioApi.getJob>>["edit_render_quality"]>(null);
  const [duckingEnabled, setDuckingEnabled] = useState(true);
  const [duckingDb, setDuckingDb] = useState("9");
  const [normalizationEnabled, setNormalizationEnabled] = useState(true);
  const [normalizationTarget, setNormalizationTarget] = useState("-18");
  const [loudnessEnabled, setLoudnessEnabled] = useState(false);
  const [targetLufs, setTargetLufs] = useState("-14");
  const [compressorEnabled, setCompressorEnabled] = useState(false);
  const [compressorThreshold, setCompressorThreshold] = useState("-18");
  const [compressorRatio, setCompressorRatio] = useState("3");
  const [eqEnabled, setEqEnabled] = useState(false);
  const [eqLow, setEqLow] = useState("0");
  const [eqMid, setEqMid] = useState("0");
  const [eqHigh, setEqHigh] = useState("0");
  const [masteringPreset, setMasteringPreset] = useState<"custom" | "voice" | "documentary" | "music" | "cinematic_sfx">("custom");
  const videoTrack = draft.tracks.find((track) => track.type === "video");
  const clips = videoTrack?.clips ?? [];
  const duration = Math.max(1, draft.duration_frames);
  const selectedClip = clips[selected] ?? null;

  useEffect(() => { setDraft(timeline); setDirty(false); setAudioDirty(false); setSelected(0); }, [timeline]);
  useEffect(() => { setRenderUrl(editedOutputUrl ?? ""); }, [editedOutputUrl]);
  useEffect(() => {
    setRenderQuality(null);
    if (!jobId) return;
    videoStudioApi.listJobAudioAssets(jobId).then(setAudioAssets).catch(() => setAudioAssets([]));
    videoStudioApi.getJob(jobId).then((job) => {
      if (job.edit_render_quality) setRenderQuality(job.edit_render_quality);
      if (job.audio_analysis) setAudioAnalysis(job.audio_analysis as Awaited<ReturnType<typeof videoStudioApi.analyzeJobAudio>>);
      if (job.audio_settings) {
        setDuckingEnabled(job.audio_settings.ducking_enabled ?? true);
        setDuckingDb(String(job.audio_settings.ducking_db ?? 9));
        setNormalizationEnabled(job.audio_settings.normalization_enabled ?? true);
        setNormalizationTarget(String(job.audio_settings.normalization_target_dbfs ?? -18));
        setLoudnessEnabled(job.audio_settings.loudness_normalization_enabled ?? false);
        setTargetLufs(String(job.audio_settings.target_lufs ?? -14));
        setCompressorEnabled(job.audio_settings.compressor_enabled ?? false);
        setCompressorThreshold(String(job.audio_settings.compressor_threshold_db ?? -18));
        setCompressorRatio(String(job.audio_settings.compressor_ratio ?? 3));
        setEqEnabled(job.audio_settings.eq_enabled ?? false);
        setEqLow(String(job.audio_settings.eq_low_db ?? 0));
        setEqMid(String(job.audio_settings.eq_mid_db ?? 0));
        setEqHigh(String(job.audio_settings.eq_high_db ?? 0));
        setMasteringPreset((job.audio_settings.mastering_preset as typeof masteringPreset) ?? "custom");
      }
    }).catch(() => undefined);
  }, [jobId]);

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
      setRenderQuality(null);
      onSaved?.(result.edit_timeline);
      setMessage("Rascunho salvo no SQLite local. Renderize para gerar o novo MP4.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Não foi possível salvar o rascunho.");
    } finally {
      setSaving(false);
    }
  }

  function updateAudioClip(role: "music" | "sound_effect", index: number, patch: Partial<EditTimelineClip>) {
    setAudioDirty(true);
    setDraft((current) => ({
      ...current,
      tracks: current.tracks.map((track) => track.role !== role ? track : {
        ...track,
        clips: track.clips.map((clip, clipIndex) => {
          if (clipIndex !== index) return clip;
          const updated = { ...clip, ...patch };
          const startFrame = patch.start_seconds !== undefined ? Math.round(patch.start_seconds * current.fps) : clip.start_frame;
          const endFrame = patch.end_seconds !== undefined ? Math.round(patch.end_seconds * current.fps) : clip.end_frame;
          return { ...updated, start_frame: startFrame, end_frame: endFrame, duration_frames: Math.max(0, endFrame - startFrame) };
        }),
      }),
    }));
  }
  function removeAudioClip(role: "music" | "sound_effect", index: number) {
    setAudioDirty(true);
    setDraft((current) => ({ ...current, tracks: current.tracks.map((track) => track.role !== role ? track : { ...track, clips: track.clips.filter((_, clipIndex) => clipIndex !== index) }) }));
  }
  async function analyzeAudio() {
    if (!jobId || dirty || audioDirty || saving || savingAudio || analyzingAudio) return;
    setAnalyzingAudio(true); setMessage("");
    try { const result = await videoStudioApi.analyzeJobAudio(jobId); setAudioAnalysis(result); setMessage(result.message); }
    catch (error) { setMessage(error instanceof Error ? error.message : "Não foi possível analisar o áudio."); }
    finally { setAnalyzingAudio(false); }
  }
  async function analyzeAvSync() {
    if (!jobId || dirty || audioDirty || saving || savingAudio || analyzingAvSync) return;
    setAnalyzingAvSync(true); setMessage("");
    try {
      const report = await videoStudioApi.analyzeJobAvSync(jobId);
      setAvSyncReport(report);
      setMessage(report.status === "passed" ? "Sincronização da timeline aprovada." : "Análise de sincronização concluída; revise os alertas.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Não foi possível analisar a sincronização.");
    } finally { setAnalyzingAvSync(false); }
  }
  async function saveAudioDraft() {
    if (!jobId || dirty || saving) return;
    const parseClip = (asset: string, start: string, end: string, volume: string, fadeIn: string, fadeOut: string, loop = false, pan = "0") => {
      if (!asset.trim()) return null;
      const startValue = Number(start);
      const endValue = Number(end);
      const volumeValue = Number(volume);
      const fadeInValue = Number(fadeIn);
      const fadeOutValue = Number(fadeOut);
      const panValue = Number(pan);
      if (![startValue, endValue, volumeValue, fadeInValue, fadeOutValue, panValue].every(Number.isFinite) ||
          startValue < 0 || endValue <= startValue || volumeValue < 0 || volumeValue > 2 ||
          fadeInValue < 0 || fadeOutValue < 0 || fadeInValue > endValue - startValue || fadeOutValue > endValue - startValue || panValue < -1 || panValue > 1) {
        throw new Error("Confira posição, fim e volume das faixas de áudio.");
      }
      return { asset: asset.trim(), start: startValue, end: endValue, volume: volumeValue, trim_start: 0, fade_in: fadeInValue, fade_out: fadeOutValue, loop, pan: panValue };
    };
    const duckingValue = Number(duckingDb);
    const normalizationValue = Number(normalizationTarget);
    if (!Number.isFinite(duckingValue) || duckingValue < 0 || duckingValue > 24) {
      setMessage("A redução do ducking deve ficar entre 0 e 24 dB.");
      return;
    }
    if (!Number.isFinite(normalizationValue) || normalizationValue < -60 || normalizationValue > 0) {
      setMessage("O alvo de normalização deve ficar entre -60 e 0 dBFS.");
      return;
    }
    const lufsValue = Number(targetLufs);
    if (!Number.isFinite(lufsValue) || lufsValue < -36 || lufsValue > -5) {
      setMessage("O alvo LUFS deve ficar entre -36 e -5 LUFS.");
      return;
    }
    const compressorThresholdValue = Number(compressorThreshold);
    const compressorRatioValue = Number(compressorRatio);
    const eqValues = [Number(eqLow), Number(eqMid), Number(eqHigh)];
    if (!Number.isFinite(compressorThresholdValue) || compressorThresholdValue < -60 || compressorThresholdValue > 0 ||
        !Number.isFinite(compressorRatioValue) || compressorRatioValue < 1 || compressorRatioValue > 20 ||
        !eqValues.every((value) => Number.isFinite(value) && value >= -12 && value <= 12)) {
      setMessage("Confira compressor (-60 a 0 dB, ratio 1 a 20) e EQ (-12 a +12 dB).");
      return;
    }
    setSavingAudio(true);
    setMessage("");
    try {
      const existingMusic = draft.tracks.find((track) => track.role === "music")?.clips ?? [];
      const existingSfx = draft.tracks.find((track) => track.role === "sound_effect")?.clips ?? [];
      const music = existingMusic.map((clip) => ({
        asset: clip.asset ?? "", start: clip.start_seconds ?? clip.start_frame / draft.fps,
        end: clip.end_seconds ?? clip.end_frame / draft.fps, volume: clip.volume ?? 1,
        trim_start: clip.trim_start ?? 0, fade_in: clip.fade_in ?? 0, fade_out: clip.fade_out ?? 0, loop: clip.loop ?? false, pan: clip.pan ?? 0,
      })).filter((clip) => clip.asset);
      const sfx = existingSfx.map((clip) => ({
        asset: clip.asset ?? "", start: clip.start_seconds ?? clip.start_frame / draft.fps,
        end: clip.end_seconds ?? clip.end_frame / draft.fps, volume: clip.volume ?? 1,
        trim_start: clip.trim_start ?? 0, fade_in: clip.fade_in ?? 0, fade_out: clip.fade_out ?? 0, pan: clip.pan ?? 0,
      })).filter((clip) => clip.asset);
      const nextMusic = parseClip(musicAsset, musicStart, musicEnd, musicVolume, musicFadeIn, musicFadeOut, musicLoop, musicPan);
      const nextSfx = parseClip(sfxAsset, sfxStart, sfxEnd, sfxVolume, sfxFadeIn, sfxFadeOut, false, sfxPan);
      if (nextMusic) music.push(nextMusic);
      if (nextSfx) sfx.push(nextSfx);
      const result = await videoStudioApi.updateJobAudio(jobId, { music_clips: music, sfx_clips: sfx, ducking_enabled: duckingEnabled, ducking_db: Number(duckingDb), ducking_threshold_db: -36, ducking_attack: 0.08, ducking_release: 0.35, normalization_enabled: normalizationEnabled, normalization_target_dbfs: Number(normalizationTarget), normalization_max_gain_db: 6, loudness_normalization_enabled: loudnessEnabled, target_lufs: Number(targetLufs), true_peak_db: -1, loudness_range: 11, compressor_enabled: compressorEnabled, compressor_threshold_db: compressorThresholdValue, compressor_ratio: compressorRatioValue, compressor_attack: 0.01, compressor_release: 0.12, compressor_makeup_db: 0, eq_enabled: eqEnabled, eq_low_db: eqValues[0], eq_mid_db: eqValues[1], eq_high_db: eqValues[2], mastering_preset: masteringPreset });
      setDraft(result.edit_timeline);
      setAudioDirty(false);
      setAudioAnalysis(null);
      setRenderQuality(null);
      onSaved?.(result.edit_timeline);
      setMusicAsset("");
      setMusicLoop(false);
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
    setRenderUrl("");
    setRenderQuality(null);
    setMessage("");
    try {
      const result = await videoStudioApi.renderJobEdits(jobId);
      setRenderUrl(result.output_url);
      setRenderQuality(result.quality ?? null);
      const duckingNote = result.ducking?.speech_detected
        ? ` Ducking aplicado: redução de ${result.ducking.reduction_db ?? 0} dB durante a narração.`
        : "";
      const normalizationNote = result.normalization?.enabled
        ? ` Normalização RMS: ${result.normalization.gain_db ?? 0} dB de ajuste, com limitador de pico.`
        : "";
      const loudnessNote = result.loudness?.enabled
        ? ` Loudness medido: ${result.loudness.output_i ?? "—"} LUFS; true peak: ${result.loudness.output_tp ?? "—"} dBTP.`
        : "";
      const masteringNote = result.mastering
        ? ` Compressor: ${result.mastering.compressor_enabled ? "ativo" : "desativado"}; EQ: ${result.mastering.eq_enabled ? "ativo" : "desativado"}.`
        : "";
      setMessage(result.message + duckingNote + normalizationNote + loudnessNote + masteringNote);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao renderizar a edição.");
      try {
        const latest = await videoStudioApi.getJob(jobId);
        if (latest.edit_render_quality) setRenderQuality(latest.edit_render_quality);
      } catch { /* Keep the original render error visible. */ }
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
              <select value={musicAsset} onChange={(event) => setMusicAsset(event.target.value)} className="mt-1 w-full rounded border bg-transparent px-2 py-1.5 text-xs"><option value="">Selecione um arquivo de áudio…</option>{audioAssets.map((asset) => <option key={asset.asset} value={asset.asset}>[{asset.folder}] {asset.name}</option>)}</select>
            </label>
            <div className="grid grid-cols-3 gap-2">
              <label className="text-xs text-surface-500">Início (s)<input type="number" min="0" value={musicStart} onChange={(event) => setMusicStart(event.target.value)} className="mt-1 w-full rounded border bg-transparent px-2 py-1" /></label>
              <label className="text-xs text-surface-500">Fim (s)<input type="number" min="0.1" value={musicEnd} onChange={(event) => setMusicEnd(event.target.value)} className="mt-1 w-full rounded border bg-transparent px-2 py-1" /></label>
              <label className="text-xs text-surface-500">Volume (0–2)<input type="number" min="0" max="2" step="0.05" value={musicVolume} onChange={(event) => setMusicVolume(event.target.value)} className="mt-1 w-full rounded border bg-transparent px-2 py-1" /></label>
              <label className="text-xs text-surface-500">Panorama L/R<input type="range" min="-1" max="1" step="0.1" value={musicPan} onChange={(event) => setMusicPan(event.target.value)} className="mt-2 w-full" /></label>
              <label className="flex items-center gap-1 text-xs text-surface-500"><input type="checkbox" checked={musicLoop} onChange={(event) => setMusicLoop(event.target.checked)} /> Repetir até o fim do clipe</label>
              <label className="text-xs text-surface-500">Fade-in (s)<input type="number" min="0" step="0.1" value={musicFadeIn} onChange={(event) => setMusicFadeIn(event.target.value)} className="mt-1 w-full rounded border bg-transparent px-2 py-1" /></label>
              <label className="text-xs text-surface-500">Fade-out (s)<input type="number" min="0" step="0.1" value={musicFadeOut} onChange={(event) => setMusicFadeOut(event.target.value)} className="mt-1 w-full rounded border bg-transparent px-2 py-1" /></label>
            </div>
          </div>
          <div className="space-y-2">
            <strong className="text-sm">🔊 Efeito sonoro</strong>
            <label className="block text-xs text-surface-500">Caminho do áudio gerado
              <select value={sfxAsset} onChange={(event) => setSfxAsset(event.target.value)} className="mt-1 w-full rounded border bg-transparent px-2 py-1.5 text-xs"><option value="">Selecione um arquivo de áudio…</option>{audioAssets.map((asset) => <option key={asset.asset} value={asset.asset}>[{asset.folder}] {asset.name}</option>)}</select>
            </label>
            <div className="grid grid-cols-3 gap-2">
              <label className="text-xs text-surface-500">Início (s)<input type="number" min="0" value={sfxStart} onChange={(event) => setSfxStart(event.target.value)} className="mt-1 w-full rounded border bg-transparent px-2 py-1" /></label>
              <label className="text-xs text-surface-500">Fim (s)<input type="number" min="0.1" value={sfxEnd} onChange={(event) => setSfxEnd(event.target.value)} className="mt-1 w-full rounded border bg-transparent px-2 py-1" /></label>
              <label className="text-xs text-surface-500">Volume (0–2)<input type="number" min="0" max="2" step="0.05" value={sfxVolume} onChange={(event) => setSfxVolume(event.target.value)} className="mt-1 w-full rounded border bg-transparent px-2 py-1" /></label>
              <label className="text-xs text-surface-500">Panorama L/R<input type="range" min="-1" max="1" step="0.1" value={sfxPan} onChange={(event) => setSfxPan(event.target.value)} className="mt-2 w-full" /></label>
              <label className="text-xs text-surface-500">Fade-in (s)<input type="number" min="0" step="0.1" value={sfxFadeIn} onChange={(event) => setSfxFadeIn(event.target.value)} className="mt-1 w-full rounded border bg-transparent px-2 py-1" /></label>
              <label className="text-xs text-surface-500">Fade-out (s)<input type="number" min="0" step="0.1" value={sfxFadeOut} onChange={(event) => setSfxFadeOut(event.target.value)} className="mt-1 w-full rounded border bg-transparent px-2 py-1" /></label>
            </div>
          </div>
          <div className="rounded-md border border-surface-200 p-3 dark:border-surface-700 sm:col-span-2">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div><strong className="text-sm">🎚️ Ducking automático da música</strong><p className="text-xs text-surface-500">Reduz a trilha quando a narração está ativa.</p></div>
              <label className="flex items-center gap-2 text-xs"><input type="checkbox" checked={duckingEnabled} onChange={(event) => { setDuckingEnabled(event.target.checked); setAudioDirty(true); }} /> Ativar ducking</label>
              <label className="text-xs text-surface-500">Redução (dB)<input type="number" min="0" max="24" step="1" value={duckingDb} onChange={(event) => { setDuckingDb(event.target.value); setAudioDirty(true); }} className="ml-2 w-20 rounded border bg-transparent px-2 py-1" /></label>
            </div>
          </div>
          <div className="rounded-md border border-surface-200 p-3 dark:border-surface-700 sm:col-span-2">
            <div className="flex flex-wrap items-center gap-4">
              <div><strong className="text-sm">🎚️ Normalização do volume final</strong><p className="text-xs text-surface-500">Ajusta o RMS médio antes do limitador; não mede LUFS e é substituída quando LUFS está ativo.</p></div>
              <label className="flex items-center gap-2 text-xs"><input type="checkbox" checked={normalizationEnabled} onChange={(event) => { setNormalizationEnabled(event.target.checked); setAudioDirty(true); }} /> Ativar normalização</label>
              <label className="text-xs text-surface-500">Alvo (dBFS)<input type="number" min="-60" max="0" step="1" value={normalizationTarget} onChange={(event) => { setNormalizationTarget(event.target.value); setAudioDirty(true); }} className="ml-2 w-20 rounded border bg-transparent px-2 py-1" /></label>
            </div>
          </div>
          <div className="rounded-md border border-surface-200 p-3 dark:border-surface-700 sm:col-span-2">
            <div className="flex flex-wrap items-center gap-4">
              <div><strong className="text-sm">📊 Loudness EBU R128 (LUFS)</strong><p className="text-xs text-surface-500">Duas passagens FFmpeg + verificação final; alvo de true peak em -1 dBTP. Requer FFmpeg com filtro loudnorm.</p></div>
              <label className="flex items-center gap-2 text-xs"><input type="checkbox" checked={loudnessEnabled} onChange={(event) => { setLoudnessEnabled(event.target.checked); setAudioDirty(true); }} /> Ativar LUFS</label>
              <label className="text-xs text-surface-500">Alvo LUFS<input type="number" min="-36" max="-5" step="1" value={targetLufs} onChange={(event) => { setTargetLufs(event.target.value); setAudioDirty(true); }} className="ml-2 w-20 rounded border bg-transparent px-2 py-1" /></label>
            </div>
          </div>
          <div className="rounded-md border border-surface-200 p-3 dark:border-surface-700 sm:col-span-2">
            <label className="block text-xs font-medium text-surface-600 dark:text-surface-300">Preset de masterização
              <select aria-label="Preset de masterização" value={masteringPreset} onChange={(event) => {
                const preset = event.target.value as typeof masteringPreset;
                setMasteringPreset(preset);
                const values = { custom: [-18, 3, 0, 0, 0], voice: [-22, 3.5, -2, 1.5, 2], documentary: [-20, 2.5, -1, 1, 1], music: [-16, 2, 1, 0, 1], cinematic_sfx: [-14, 3, 2, -1, 1] }[preset];
                setCompressorEnabled(preset !== "custom"); setCompressorThreshold(String(values[0])); setCompressorRatio(String(values[1]));
                setEqEnabled(preset !== "custom"); setEqLow(String(values[2])); setEqMid(String(values[3])); setEqHigh(String(values[4])); setAudioDirty(true);
              }} className="mt-1 w-full rounded border bg-transparent px-2 py-2">
                <option value="custom">Personalizado</option><option value="voice">Voz clara</option><option value="documentary">Documentário</option><option value="music">Música</option><option value="cinematic_sfx">Efeitos cinematográficos</option>
              </select>
            </label>
            <p className="mt-2 text-[11px] text-surface-500">Os presets aplicam compressor e EQ automaticamente. Escolha Personalizado para ajustar manualmente.</p>
          </div>
          <div className="rounded-md border border-surface-200 p-3 dark:border-surface-700 sm:col-span-2">
            <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
              <div><strong className="text-sm">🎛️ Compressor de dinâmica</strong><p className="text-xs text-surface-500">Controla picos e reduz variações de volume com ganho estéreo vinculado.</p></div>
              <label className="flex items-center gap-2 text-xs"><input type="checkbox" checked={compressorEnabled} onChange={(event) => { setCompressorEnabled(event.target.checked); setAudioDirty(true); }} /> Ativar compressor</label>
            </div>
            <div className="grid gap-3 sm:grid-cols-2">
              <label className="text-xs text-surface-500">Threshold (dB)<input type="number" min="-60" max="0" value={compressorThreshold} onChange={(event) => { setCompressorThreshold(event.target.value); setAudioDirty(true); }} className="mt-1 w-full rounded border bg-transparent px-2 py-1" /></label>
              <label className="text-xs text-surface-500">Ratio (1:1 a 20:1)<input type="number" min="1" max="20" step="0.5" value={compressorRatio} onChange={(event) => { setCompressorRatio(event.target.value); setAudioDirty(true); }} className="mt-1 w-full rounded border bg-transparent px-2 py-1" /></label>
            </div>
            <p className="mt-2 text-[11px] text-surface-500">Attack 10 ms · Release 120 ms · Makeup 0 dB.</p>
          </div>
          <div className="rounded-md border border-surface-200 p-3 dark:border-surface-700 sm:col-span-2">
            <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
              <div><strong className="text-sm">🎚️ Equalizador de 3 bandas</strong><p className="text-xs text-surface-500">Graves, médios e agudos com transições suaves; ajuste de -12 a +12 dB.</p></div>
              <label className="flex items-center gap-2 text-xs"><input type="checkbox" checked={eqEnabled} onChange={(event) => { setEqEnabled(event.target.checked); setAudioDirty(true); }} /> Ativar EQ</label>
            </div>
            <div className="grid gap-3 sm:grid-cols-3">
              <label className="text-xs text-surface-500">Graves: {Number(eqLow).toFixed(1)} dB<input aria-label="Graves" type="range" min="-12" max="12" step="0.5" value={eqLow} onChange={(event) => { setEqLow(event.target.value); setAudioDirty(true); }} className="mt-2 w-full" /></label>
              <label className="text-xs text-surface-500">Médios: {Number(eqMid).toFixed(1)} dB<input aria-label="Médios" type="range" min="-12" max="12" step="0.5" value={eqMid} onChange={(event) => { setEqMid(event.target.value); setAudioDirty(true); }} className="mt-2 w-full" /></label>
              <label className="text-xs text-surface-500">Agudos: {Number(eqHigh).toFixed(1)} dB<input aria-label="Agudos" type="range" min="-12" max="12" step="0.5" value={eqHigh} onChange={(event) => { setEqHigh(event.target.value); setAudioDirty(true); }} className="mt-2 w-full" /></label>
            </div>
          </div>
          {(["music", "sound_effect"] as const).map((role) => {
            const track = draft.tracks.find((item) => item.role === role);
            return track?.clips.map((clip, index) => (
              <div key={role + "-" + index} className="grid gap-2 rounded-md bg-surface-50 p-2 dark:bg-surface-800 sm:col-span-2 sm:grid-cols-[minmax(140px,2fr)_repeat(5,minmax(70px,1fr))_auto]">
                <label className="text-[11px] text-surface-500">{role === "music" ? "Música" : "Efeito"} · arquivo<select value={clip.asset ?? ""} onChange={(event) => updateAudioClip(role, index, { asset: event.target.value })} className="mt-1 w-full rounded border bg-transparent px-2 py-1.5 text-xs"><option value="">Selecione…</option>{audioAssets.map((asset) => <option key={asset.asset} value={asset.asset}>{asset.name}</option>)}</select></label>
                <label className="text-[11px] text-surface-500">Início (s)<input type="number" min="0" step="0.1" value={clip.start_seconds ?? clip.start_frame / draft.fps} onChange={(event) => updateAudioClip(role, index, { start_seconds: Number(event.target.value) })} className="mt-1 w-full rounded border bg-transparent px-2 py-1" /></label>
                <label className="text-[11px] text-surface-500">Fim (s)<input type="number" min="0.1" step="0.1" value={clip.end_seconds ?? clip.end_frame / draft.fps} onChange={(event) => updateAudioClip(role, index, { end_seconds: Number(event.target.value) })} className="mt-1 w-full rounded border bg-transparent px-2 py-1" /></label>
                <label className="text-[11px] text-surface-500">Volume<input type="number" min="0" max="2" step="0.05" value={clip.volume ?? 1} onChange={(event) => updateAudioClip(role, index, { volume: Number(event.target.value) })} className="mt-1 w-full rounded border bg-transparent px-2 py-1" /></label>
                <label className="text-[11px] text-surface-500">Panorama L/R ({(clip.pan ?? 0).toFixed(1)})<input type="range" min="-1" max="1" step="0.1" value={clip.pan ?? 0} onChange={(event) => updateAudioClip(role, index, { pan: Number(event.target.value) })} className="mt-2 w-full" /></label>
                {role === "music" && <label className="flex items-center gap-1 self-end text-[11px] text-surface-500"><input type="checkbox" checked={clip.loop ?? false} onChange={(event) => updateAudioClip(role, index, { loop: event.target.checked })} /> Repetir</label>}
                <label className="text-[11px] text-surface-500">Corte (s)<input type="number" min="0" step="0.1" value={clip.trim_start ?? 0} onChange={(event) => updateAudioClip(role, index, { trim_start: Number(event.target.value) })} className="mt-1 w-full rounded border bg-transparent px-2 py-1" /></label>
                <label className="text-[11px] text-surface-500">Fade-in (s)<input type="number" min="0" step="0.1" value={clip.fade_in ?? 0} onChange={(event) => updateAudioClip(role, index, { fade_in: Number(event.target.value) })} className="mt-1 w-full rounded border bg-transparent px-2 py-1" /></label>
                <button type="button" onClick={() => removeAudioClip(role, index)} className="self-end rounded border border-red-300 px-2 py-1 text-xs text-red-600">Remover</button>
                <label className="text-[11px] text-surface-500 sm:col-start-6">Fade-out (s)<input type="number" min="0" step="0.1" value={clip.fade_out ?? 0} onChange={(event) => updateAudioClip(role, index, { fade_out: Number(event.target.value) })} className="mt-1 w-full rounded border bg-transparent px-2 py-1" /></label>
              </div>
            ));
          })}
          <div className="flex flex-wrap items-center gap-2 sm:col-span-2">
            <button type="button" onClick={analyzeAudio} disabled={!jobId || dirty || audioDirty || saving || savingAudio || analyzingAudio} className="rounded-md border border-primary-300 px-3 py-2 text-xs font-semibold disabled:opacity-40 dark:border-primary-700">
              {analyzingAudio ? "Analisando áudio…" : "Analisar áudio"}
            </button>
            <button type="button" onClick={analyzeAvSync} disabled={!jobId || dirty || audioDirty || saving || savingAudio || analyzingAvSync} className="rounded-md border border-primary-300 px-3 py-2 text-xs font-semibold disabled:opacity-40 dark:border-primary-700">
              {analyzingAvSync ? "Verificando sincronização…" : "Verificar A/V"}
            </button>
            <button type="button" onClick={saveAudioDraft} disabled={savingAudio || dirty || saving || (!audioDirty && !musicAsset.trim() && !sfxAsset.trim())} className="rounded-md border border-surface-300 px-3 py-2 text-xs font-semibold disabled:opacity-40 dark:border-surface-600">
              {savingAudio ? "Salvando áudio…" : audioDirty ? "Salvar alterações de áudio" : "Salvar faixas de áudio"}
            </button>
            <span className="text-[11px] text-surface-400">A lista mostra arquivos gerados em music, effects, voice, dubbing e mix. Caminhos externos são bloqueados.</span>
          </div>
          {avSyncReport && <div className="rounded-md border border-surface-200 p-3 text-xs dark:border-surface-700 sm:col-span-2">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <strong>Sincronização de áudio e vídeo</strong>
              <span className={avSyncReport.status === "passed" ? "text-emerald-600" : avSyncReport.status === "blocked" ? "text-red-600" : "text-amber-600"}>{avSyncReport.status.replaceAll("_", " ")}</span>
            </div>
            <p className="mt-1 text-surface-500">{avSyncReport.video_scene_count} cenas · {avSyncReport.narration_clip_count} clipes de narração · {avSyncReport.fps} FPS</p>
            {avSyncReport.scene_comparisons.length > 0 && <ul className="mt-2 space-y-1">{avSyncReport.scene_comparisons.map((item) => <li key={item.scene_index}>Cena {item.scene_index + 1}: início {item.start_delta_ms > 0 ? "+" : ""}{item.start_delta_ms} ms · fim {item.end_delta_ms > 0 ? "+" : ""}{item.end_delta_ms} ms · {item.aligned ? "alinhada" : "revisar"}</li>)}</ul>}
            {avSyncReport.warnings.length > 0 && <ul className="mt-2 list-disc space-y-1 pl-5 text-amber-600">{avSyncReport.warnings.map((warning, index) => <li key={index}>{warning.code.replaceAll("_", " ")}</li>)}</ul>}
            <p className="mt-2 text-surface-400">Verificação baseada nos frames da timeline; não mede sincronização labial nem o início acústico real da fala.</p>
          </div>}
          {audioAnalysis && <div className="rounded-md border border-surface-200 p-3 text-xs dark:border-surface-700 sm:col-span-2">
            <div className="flex flex-wrap items-center justify-between gap-2"><strong>Relatório de inteligência de áudio</strong><span>{audioAnalysis.sources_analyzed} arquivo(s) analisado(s)</span></div>
            {audioAnalysis.warnings.length > 0 ? <ul className="mt-2 list-disc space-y-1 pl-5 text-amber-600">{audioAnalysis.warnings.map((warning, index) => <li key={index}>{warning.role}: {warning.code.replaceAll("_", " ")}</li>)}</ul> : <p className="mt-2 text-emerald-600">Nenhum alerta detectado nas fontes analisadas.</p>}
            {audioAnalysis.ducking_recommendation.available && <div className="mt-3 flex flex-wrap items-center justify-between gap-2 rounded bg-surface-50 p-2 dark:bg-surface-800">
              <span>Redução sugerida: <strong>{audioAnalysis.ducking_recommendation.recommended_ducking_db} dB</strong> · Limiar: <strong>{audioAnalysis.ducking_recommendation.recommended_threshold_db} dB</strong></span>
              <button type="button" onClick={() => { setDuckingEnabled(true); setDuckingDb(String(audioAnalysis.ducking_recommendation.recommended_ducking_db)); setAudioDirty(true); setMessage("Sugestão de ducking aplicada ao rascunho. Salve as faixas para persistir."); }} className="rounded border px-2 py-1 font-semibold">Aplicar sugestão</button>
            </div>}
            <p className="mt-2 text-[11px] text-surface-500">{audioAnalysis.ducking_recommendation.reason}</p>
          </div>}
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
          <button type="button" onClick={saveDraft} disabled={saving || !dirty || audioDirty} className="rounded-md border border-surface-300 px-3 py-2 text-xs font-semibold disabled:opacity-40 dark:border-surface-600">
            {saving ? "Salvando…" : "Salvar rascunho"}
          </button>
          <button type="button" onClick={renderEdits} disabled={rendering || saving || dirty || audioDirty || savingAudio} className="rounded-md bg-primary-600 px-3 py-2 text-xs font-semibold text-white disabled:opacity-40">
            {rendering ? "Renderizando MP4…" : "Renderizar edição"}
          </button>
        </>}
      </div>
      {message && <p role="status" className="mt-2 text-xs text-surface-500">{message}</p>}
      {renderUrl && <p className="mt-2 text-xs"><a className="text-primary-600 underline" href={renderUrl} target="_blank" rel="noreferrer">Abrir MP4 renderizado</a></p>}
      {renderQuality && <div className="mt-3 rounded-md border border-surface-200 p-3 text-xs dark:border-surface-700" aria-label="Qualidade do áudio exportado">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <strong>Controle de qualidade do áudio</strong>
          <span className={renderQuality.status === "blocked" ? "font-semibold text-red-600" : renderQuality.status === "needs_review" ? "font-semibold text-amber-600" : "font-semibold text-emerald-600"}>
            {renderQuality.status === "blocked" ? "Exportação bloqueada" : renderQuality.status === "needs_review" ? "Revisão recomendada" : "Verificação aprovada"}
          </span>
        </div>
        <div className="mt-2 grid grid-cols-2 gap-2 sm:grid-cols-4">
          <span>Pico final: <strong>{renderQuality.peak_dbfs ?? "—"} dBFS</strong></span>
          <span>RMS: <strong>{renderQuality.rms_dbfs ?? "—"} dBFS</strong></span>
          <span>Clipping: <strong>{renderQuality.clipping_ratio ?? "—"}</strong></span>
          <span>Alertas: <strong>{renderQuality.warnings?.length ?? 0}</strong></span>
        </div>
        {!!renderQuality.warnings?.length && <ul className="mt-2 list-disc space-y-1 pl-5 text-amber-600">{renderQuality.warnings.map((warning, index) => <li key={index}>{warning.message}</li>)}</ul>}
        {!!renderQuality.recommendations?.length && <div className="mt-3 space-y-2">
          <strong>Correções sugeridas</strong>
          {renderQuality.recommendations.map((recommendation, index) => <div key={index} className="flex flex-wrap items-center justify-between gap-2 rounded bg-surface-50 p-2 dark:bg-surface-800">
            <span>{recommendation.message}</span>
            {recommendation.action === "increase_ducking" && <button type="button" onClick={() => { setDuckingEnabled(true); setDuckingDb(String(recommendation.recommended_ducking_db ?? 12)); setAudioDirty(true); setMessage("Ducking atualizado no rascunho. Salve as faixas antes de renderizar novamente."); }} className="rounded border px-2 py-1 font-semibold">Aplicar correção</button>}
          </div>)}
        </div>}
        {!!renderQuality.silence_gaps?.length && <p className="mt-2">Silêncios internos: {renderQuality.silence_gaps.map((gap) => String(gap.start) + "s–" + String(gap.end) + "s").join(", ")}</p>}
        {!!renderQuality.narration_music_masking?.length && <p className="mt-2">Possível voz encoberta: {renderQuality.narration_music_masking.map((gap) => String(gap.start) + "s–" + String(gap.end) + "s").join(", ")}</p>}
        <p className="mt-2 text-[10px] text-surface-500">{renderQuality.masking_method}</p>
      </div>}
      <p className="mt-2 text-[11px] text-surface-400">
        O rascunho fica no SQLite local. Música, efeitos e narração por cena são mixados na renderização; uma faixa única original não é reposicionada automaticamente.
      </p>
    </section>
  );
}
