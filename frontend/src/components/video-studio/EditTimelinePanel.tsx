"use client";

import { useEffect, useMemo, useState } from "react";
import { videoStudioApi, type EditTimeline, type EditTimelineClip, type StudioAudioAsset, type SceneImageAsset, type SceneVisualDirection, type SceneImageSimilarityReport } from "@/api/videoStudio";

type Props = {
  timeline: EditTimeline;
  jobId?: string;
  editedOutputUrl?: string | null;
  sceneAssets?: SceneImageAsset[] | null;
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

export default function EditTimelinePanel({ timeline, jobId, editedOutputUrl, sceneAssets, title = "Editor de timeline", onSaved }: Props) {
  const [draft, setDraft] = useState<EditTimeline>(timeline);
  const [sceneImageAssets, setSceneImageAssets] = useState<SceneImageAsset[]>(sceneAssets ?? []);
  const [sceneImageCandidates, setSceneImageCandidates] = useState<Record<number, SceneImageAsset & { candidate_id: string }>>({});
  const [approvingImageScene, setApprovingImageScene] = useState<number | null>(null);
  const [sceneImagePrompts, setSceneImagePrompts] = useState<Record<number, string>>({});
  const [visualDirections, setVisualDirections] = useState<Record<number, SceneVisualDirection>>({});
  const [continuityReport, setContinuityReport] = useState<import("@/api/videoStudio").SceneContinuityReport | null>(null);
  const [editingImageScene, setEditingImageScene] = useState<number | null>(null);
  const [selectedImageScenes, setSelectedImageScenes] = useState<number[]>([]);
  const [regeneratingImageBatch, setRegeneratingImageBatch] = useState(false);
  const [generatingMotionScene, setGeneratingMotionScene] = useState<number | null>(null);
  const [generatedMotionClips, setGeneratedMotionClips] = useState<Record<number, string>>({});
  const [imageDenoisingStrength, setImageDenoisingStrength] = useState(0.45);
  const [selected, setSelected] = useState<number>(0);
  const [playheadFrame, setPlayheadFrame] = useState(0);
  const [saving, setSaving] = useState(false);
  const [rendering, setRendering] = useState(false);
  const [previewing, setPreviewing] = useState(false);
  const [previewUrl, setPreviewUrl] = useState("");
  const [renderUrl, setRenderUrl] = useState(editedOutputUrl ?? "");
  const [outputValidation, setOutputValidation] = useState<Awaited<ReturnType<typeof videoStudioApi.validateJobOutput>> | null>(null);
  const [assetHealth, setAssetHealth] = useState<Awaited<ReturnType<typeof videoStudioApi.getJobAssetHealth>> | null>(null);\n  const [checkingAssetHealth, setCheckingAssetHealth] = useState(false);
  const [dependencyGraph, setDependencyGraph] = useState<Awaited<ReturnType<typeof videoStudioApi.getJobDependencyGraph>> | null>(null);
  const [loadingDependencyGraph, setLoadingDependencyGraph] = useState(false);
  const [message, setMessage] = useState("");
  const [staleVidGridClipCount, setStaleVidGridClipCount] = useState(0);
  const [vidGridRecoveryPlan, setVidGridRecoveryPlan] = useState<Awaited<ReturnType<typeof videoStudioApi.getVidGridRecoveryPlan>> | null>(null);
  const [rebuildingVidGridClips, setRebuildingVidGridClips] = useState(false);
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
  const [audioDirty, setAudioDirty] = useState(false);
  const [audioAnalysis, setAudioAnalysis] = useState<Awaited<ReturnType<typeof videoStudioApi.analyzeJobAudio>> | null>(null);
  const [analyzingAudio, setAnalyzingAudio] = useState(false);
  const [avSyncReport, setAvSyncReport] = useState<Awaited<ReturnType<typeof videoStudioApi.analyzeJobAvSync>> | null>(null);
  const [analyzingAvSync, setAnalyzingAvSync] = useState(false);
  const [visualReport, setVisualReport] = useState<Awaited<ReturnType<typeof videoStudioApi.analyzeJobVisuals>> | null>(null);
  const [analyzingVisuals, setAnalyzingVisuals] = useState(false);
  const [mp4VisualReport, setMp4VisualReport] = useState<Awaited<ReturnType<typeof videoStudioApi.analyzeJobMp4Visuals>> | null>(null);
  const [imageSimilarityReport, setImageSimilarityReport] = useState<SceneImageSimilarityReport | null>(null);
  const [analyzingImageSimilarity, setAnalyzingImageSimilarity] = useState(false);
  const [analyzingMp4Visuals, setAnalyzingMp4Visuals] = useState(false);

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

  useEffect(() => {
    if (!jobId) return;
    let cancelled = false;
    videoStudioApi.getJobVisualDirection(jobId).then((result) => {
      if (cancelled) return;
      const byIndex: Record<number, SceneVisualDirection> = {};
      const suggestedPrompts: Record<number, string> = {};
      for (const scene of result.scenes) {
        byIndex[scene.scene_index] = scene;
        const preferredPrompt = scene.visual_prompt_full || scene.visual_prompt_suggestion || scene.visual_prompt;
        if (preferredPrompt) suggestedPrompts[scene.scene_index] = preferredPrompt;
      }
      setVisualDirections(byIndex);
      setContinuityReport(result.storyboard_report?.continuity_report ?? null);
      setSceneImagePrompts((current) => ({ ...suggestedPrompts, ...current }));
    }).catch(() => {
      // Older jobs may not have retained scene direction metadata.
    });
    return () => { cancelled = true; };
  }, [jobId]);
  useEffect(() => { setDraft(timeline); setDirty(false); setAudioDirty(false); setSelected(0); }, [timeline]);
  useEffect(() => { setSceneImageAssets(sceneAssets ?? []); }, [sceneAssets]);
  useEffect(() => { setRenderUrl(editedOutputUrl ?? ""); }, [editedOutputUrl]);
  useEffect(() => {
    setRenderQuality(null);
    if (!jobId) return;
    videoStudioApi.listJobAudioAssets(jobId).then(setAudioAssets).catch(() => setAudioAssets([]));
    videoStudioApi.getJob(jobId).then((job) => {
      if (job.scene_assets) setSceneImageAssets(job.scene_assets);
      if (job.scene_image_candidates) {
        const pending: Record<number, SceneImageAsset & { candidate_id: string }> = {};
        for (const items of Object.values(job.scene_image_candidates)) {
          for (const item of items) pending[item.scene_index] = item;
        }
        setSceneImageCandidates(pending);
      }
      if (job.vidgrid_compatible) {
        videoStudioApi.getVidGridRecoveryPlan(jobId).then((plan) => {
          setVidGridRecoveryPlan(plan);
          setStaleVidGridClipCount(plan.repairable_count);
        }).catch(() => setVidGridRecoveryPlan(null));
      } else {
        setVidGridRecoveryPlan(null);
        setStaleVidGridClipCount(0);
      }
      if (job.scene_clips?.length) {
        setGeneratedMotionClips(Object.fromEntries(
          job.scene_clips
            .filter((clip) => clip.generative_video_url)
            .map((clip) => [clip.scene_index, clip.generative_video_url as string]),
        ));
      }
      if (job.edit_render_quality) setRenderQuality(job.edit_render_quality);
      if (job.audio_analysis) setAudioAnalysis(job.audio_analysis as Awaited<ReturnType<typeof videoStudioApi.analyzeJobAudio>>);
      if (job.av_sync_analysis) setAvSyncReport(job.av_sync_analysis as Awaited<ReturnType<typeof videoStudioApi.analyzeJobAvSync>>);
      if (job.visual_intelligence) setVisualReport(job.visual_intelligence as Awaited<ReturnType<typeof videoStudioApi.analyzeJobVisuals>>);
      if (job.mp4_visual_analysis) setMp4VisualReport(job.mp4_visual_analysis as Awaited<ReturnType<typeof videoStudioApi.analyzeJobMp4Visuals>>);
      if (job.image_similarity_analysis) setImageSimilarityReport(job.image_similarity_analysis);
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
  async function analyzeVisuals() {
    if (!jobId || dirty || audioDirty || saving || savingAudio || analyzingVisuals) return;
    setAnalyzingVisuals(true); setMessage("");
    try {
      const report = await videoStudioApi.analyzeJobVisuals(jobId);
      setVisualReport(report);
      setMessage(report.status === "good" ? "Análise visual concluída sem alertas." : "Análise visual concluída; revise os pontos indicados.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Não foi possível analisar a qualidade visual.");
    } finally { setAnalyzingVisuals(false); }
  }
  async function analyzeSceneImageSimilarity() {
    if (!jobId || dirty || audioDirty || saving || savingAudio || analyzingImageSimilarity) return;
    setAnalyzingImageSimilarity(true); setMessage("");
    try {
      const report = await videoStudioApi.analyzeJobSceneImageSimilarity(jobId);
      setImageSimilarityReport(report);
      setMessage(report.status === "duplicates_found" ? "Foram encontrados " + report.duplicate_pairs.length + " pares de imagens semelhantes. Revise antes de substituir." : "Nenhum par duplicado foi detectado nas imagens disponíveis.");
    } catch (error) { setMessage(error instanceof Error ? error.message : "Não foi possível comparar as imagens das cenas."); }
    finally { setAnalyzingImageSimilarity(false); }
  }

  async function analyzeMp4Visuals() {
    if (!jobId || dirty || audioDirty || saving || savingAudio || analyzingMp4Visuals) return;
    setAnalyzingMp4Visuals(true); setMessage("");
    try {
      const report = await videoStudioApi.analyzeJobMp4Visuals(jobId);
      setMp4VisualReport(report);
      setMessage(report.status === "no_obvious_issue" ? "Análise dos frames concluída sem alertas detectados." : "Análise do MP4 concluída; revise os trechos sinalizados.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Não foi possível analisar os frames do MP4.");
    } finally { setAnalyzingMp4Visuals(false); }
  }
  async function editSceneImage(sceneIndex: number) {
    if (!jobId) return;
    const prompt = (sceneImagePrompts[sceneIndex] ?? "").trim();
    if (!prompt || editingImageScene !== null) return;
    setEditingImageScene(sceneIndex); setMessage("");
    try {
      const result = await videoStudioApi.editSceneImage(jobId, sceneIndex, { prompt, denoising_strength: imageDenoisingStrength, stage_only: true });
      if (!result.candidate_id) throw new Error("O servidor não retornou o identificador da imagem candidata.");
      setSceneImageCandidates((current) => ({ ...current, [sceneIndex]: {
        scene_index: sceneIndex, candidate_id: result.candidate_id!, image_path: result.image_path,
        image_url: result.image_url, provider: result.provider, status: "candidate",
        operation: result.operation, prompt: result.prompt, approval_required: true,
      } }));
      setMessage(`Nova imagem da cena ${sceneIndex + 1} gerada como candidata. Compare com a atual e aprove para aplicar.`);
    } catch (error) { setMessage(error instanceof Error ? error.message : "Não foi possível gerar a imagem candidata."); }
    finally { setEditingImageScene(null); }
  }

  async function approveSceneImage(sceneIndex: number) {
    if (!jobId || approvingImageScene !== null) return;
    const candidate = sceneImageCandidates[sceneIndex];
    if (!candidate) return;
    setApprovingImageScene(sceneIndex);
    try {
      const result = await videoStudioApi.approveSceneImageCandidate(jobId, sceneIndex, candidate.candidate_id);
      setSceneImageAssets((current) => [...current.filter((asset) => asset.scene_index !== sceneIndex), { ...candidate, status: "edited", approval_required: false }]);
      setVisualDirections((current) => current[sceneIndex] ? { ...current, [sceneIndex]: { ...current[sceneIndex], image_url: result.image_url, image_status: "edited" } } : current);
      setSceneImageCandidates((current) => { const next = { ...current }; delete next[sceneIndex]; return next; });
      videoStudioApi.getJob(jobId).then((latestJob) => {
        videoStudioApi.getVidGridRecoveryPlan(jobId).then((plan) => {
          setVidGridRecoveryPlan(plan);
          setStaleVidGridClipCount(plan.repairable_count);
        }).catch(() => undefined);
      }).catch(() => undefined);
      setMessage(result.message);
    } catch (error) { setMessage(error instanceof Error ? error.message : "Não foi possível aprovar a imagem candidata."); }
    finally { setApprovingImageScene(null); }
  }

  async function discardSceneImage(sceneIndex: number) {
    if (!jobId) return;
    const candidate = sceneImageCandidates[sceneIndex];
    if (!candidate) return;
    try {
      await videoStudioApi.discardSceneImageCandidate(jobId, sceneIndex, candidate.candidate_id);
      setSceneImageCandidates((current) => { const next = { ...current }; delete next[sceneIndex]; return next; });
      setMessage("Candidata descartada. A imagem atual da cena foi mantida.");
    } catch (error) { setMessage(error instanceof Error ? error.message : "Não foi possível descartar a candidata."); }
  }

  async function regenerateSelectedImages(sceneIndices: number[] = selectedImageScenes) {
    if (!jobId || regeneratingImageBatch || editingImageScene !== null) return;
    const selectedScenes = sceneIndices.map((sceneIndex) => {
      const direction = visualDirections[sceneIndex];
      const authored = String(sceneImagePrompts[sceneIndex] ?? "").trim();
      const prompt = authored || direction?.visual_prompt_full || direction?.visual_prompt_suggestion || direction?.visual_prompt
        || (direction?.narration ? `Ilustração fiel desta narração: ${direction.narration}. ${direction.visual_direction ?? ""}` : "");
      return { scene_index: sceneIndex, prompt: prompt.trim() };
    });
    const missing = selectedScenes.filter((scene) => !scene.prompt);
    if (missing.length) { setMessage(`Adicione um prompt para as cenas: ${missing.map((scene) => scene.scene_index + 1).join(", ")}.`); return; }
    if (!selectedScenes.length) return;
    setRegeneratingImageBatch(true); setMessage("");
    try {
      const response = await videoStudioApi.regenerateSelectedSceneImages(jobId, selectedScenes);
      const successful = response.results.filter((item) => item.status === "candidate" && item.result);
      setSceneImageCandidates((current) => {
        const next = { ...current };
        for (const item of successful) {
          const result = item.result!;
          if (!result.candidate_id) continue;
          next[item.scene_index] = { scene_index: item.scene_index, candidate_id: result.candidate_id,
            image_path: result.image_path, image_url: result.image_url, provider: result.provider,
            status: "candidate", operation: result.operation, prompt: result.prompt, approval_required: true };
        }
        return next;
      });
      setSelectedImageScenes([]);
      setMessage(response.message + (response.failed ? ` Falhas: ${response.results.filter((item) => item.status === "failed").map((item) => `cena ${item.scene_index + 1}: ${item.error}`).join("; ")}` : ""));
    } catch (error) { setMessage(error instanceof Error ? error.message : "Não foi possível regenerar as cenas selecionadas."); }
    finally { setRegeneratingImageBatch(false); }
  }

  async function generateSceneMotion(sceneIndex: number, asset: SceneImageAsset) {
    if (!asset.image_path || generatingMotionScene !== null) return;
    setGeneratingMotionScene(sceneIndex);
    setMessage("");
    try {
      if (!jobId) throw new Error("Projeto não identificado.");
      const sourceSceneIndex = sceneOrder[sceneIndex] ?? sceneIndex;
      const result = await videoStudioApi.generateJobSceneMotion(jobId, sourceSceneIndex, {
        motion_prompt: (sceneImagePrompts[sceneIndex] || asset.visual_prompt || asset.prompt || "Create natural cinematic movement while preserving the scene subject").trim(),
        negative_prompt: "flicker, unstable identity, deformation, extra limbs, text, watermark",
      });
      setGeneratedMotionClips((current) => ({ ...current, [sourceSceneIndex]: result.download_url }));
      setMessage(`Clipe generativo da cena ${sceneIndex + 1} integrado ao projeto. Salve a timeline e renderize para incluí-lo no MP4 final.`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Não foi possível gerar o movimento por IA. Verifique o ComfyUI e o workflow configurado.");
    } finally {
      setGeneratingMotionScene(null);
    }
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

  async function previewEdits() {
    if (!jobId || dirty || audioDirty || saving || savingAudio || rendering) return;
    setPreviewing(true);
    setPreviewUrl("");
    setMessage("");
    try {
      const result = await videoStudioApi.previewJobEdits(jobId);
      setPreviewUrl(result.preview_url);
      setMessage(`${result.message} ${result.width}×${result.height} · ${result.fps} FPS · ${formatTime(result.duration)}.`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao gerar a prévia visual.");
    } finally {
      setPreviewing(false);
    }
  }

  async function rebuildStaleVidGridClips() {
    if (!jobId || rebuildingVidGridClips || rendering || dirty || audioDirty) return;
    setRebuildingVidGridClips(true);
    setMessage("Reconstruindo somente os clipes desatualizados de 10 segundos…");
    try {
      const result = await videoStudioApi.rebuildStaleVidGridClips(jobId);
      const latest = await videoStudioApi.getJob(jobId);
      const plan = await videoStudioApi.getVidGridRecoveryPlan(jobId);
      setVidGridRecoveryPlan(plan);
      setStaleVidGridClipCount(plan.repairable_count);
      if (latest.scene_assets) setSceneImageAssets(latest.scene_assets);
      setMessage(result.message || `${result.rebuilt} clipe(s) reconstruído(s); ${result.failed} falha(s).`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao reconstruir os clipes desatualizados.");
    } finally {
      setRebuildingVidGridClips(false);
    }
  }

  async function checkAssetHealth() {
    if (!jobId) return;
    setCheckingAssetHealth(true);
    try {
      const report = await videoStudioApi.getJobAssetHealth(jobId);
      setAssetHealth(report);
      setMessage(report.status === "healthy"
        ? "Todos os ativos referenciados foram encontrados e lidos."
        : "A auditoria encontrou ativos que precisam de atenção.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao auditar os ativos do projeto.");
    } finally {
      setCheckingAssetHealth(false);
    }
  }

  async function loadDependencyGraph() {
    if (!jobId) return;
    setLoadingDependencyGraph(true);
    try {
      const graph = await videoStudioApi.getJobDependencyGraph(jobId);
      setDependencyGraph(graph);
      setMessage(`Mapa de dependências carregado: ${graph.summary.nodes} ativos e ${graph.summary.dependencies} relações.`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao montar o mapa de dependências.");
    } finally {
      setLoadingDependencyGraph(false);
    }
  }

  async function validateOutput() {
    if (!jobId) return;
    try {
      const report = await videoStudioApi.validateJobOutput(jobId);
      setOutputValidation(report);
      setMessage(report.valid ? "MP4 validado estruturalmente." : "Validação encontrou alertas ou falhas; confira o relatório.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao validar MP4.");
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

      {jobId && <section className="mb-4 rounded-lg border border-surface-200 p-3 dark:border-surface-700">
        <div className="mb-3">
          <h3 className="text-sm font-semibold text-surface-900 dark:text-surface-100">Imagens por cena · edição com texto</h3>
          <p className="mt-1 text-xs text-surface-500">Descreva a alteração desejada. A IA edita a imagem existente ou cria uma imagem nova para a cena. Depois, use Renderizar edição para atualizar o MP4.</p>
        </div>
        <label className="mb-3 block max-w-sm text-xs text-surface-500">
          Força da alteração · {imageDenoisingStrength.toFixed(2)}
          <input type="range" min={0.05} max={0.95} step={0.05} value={imageDenoisingStrength} onChange={(event) => setImageDenoisingStrength(Number(event.target.value))} className="mt-1 w-full accent-primary-600" />
          <span className="flex justify-between text-[10px]"><span>Preservar imagem</span><span>Transformar bastante</span></span>
        </label>
        <div className="mb-3 flex flex-wrap items-center justify-between gap-2 rounded-md bg-surface-50 p-2 dark:bg-surface-800">
          <label className="flex items-center gap-2 text-xs text-surface-600 dark:text-surface-300">
            <input type="checkbox" checked={clips.length > 0 && clips.every((clip, index) => selectedImageScenes.includes(clip.source_scene_index ?? clip.scene_index ?? index))} onChange={(event) => setSelectedImageScenes(event.target.checked ? clips.map((clip, index) => clip.source_scene_index ?? clip.scene_index ?? index) : [])} />
            Selecionar todas as cenas
          </label>
          <div className="flex flex-wrap gap-2">
            <button type="button" onClick={() => regenerateSelectedImages(clips.map((clip, index) => clip.source_scene_index ?? clip.scene_index ?? index))} disabled={!clips.length || regeneratingImageBatch || editingImageScene !== null} className="rounded-md border border-primary-600 px-3 py-2 text-xs font-semibold text-primary-700 dark:text-primary-300 disabled:opacity-40">
              Gerar imagens de todas as cenas pelo roteiro
            </button>
            <button type="button" onClick={() => regenerateSelectedImages()} disabled={!selectedImageScenes.length || regeneratingImageBatch || editingImageScene !== null} className="rounded-md bg-primary-600 px-3 py-2 text-xs font-semibold text-white disabled:opacity-40">
              {regeneratingImageBatch ? "Regenerando cenas…" : `Regenerar selecionadas (${selectedImageScenes.length})`}
            </button>
          </div>
        </div>
        <div className="grid gap-3 sm:grid-cols-2">
          {(draft.tracks.find((track) => track.type === "video")?.clips ?? []).map((clip) => {
            const index = clip.scene_index ?? 0;
            const sourceIndex = clip.source_scene_index ?? index;
            const asset = sceneImageAssets.find((item) => item.scene_index === sourceIndex);
            return <div key={index} className="rounded-lg border border-surface-200 p-2 dark:border-surface-700">
              {asset?.image_url ? <img src={asset.image_url} alt={`Imagem da cena ${index + 1}`} className="mb-2 aspect-video w-full rounded-md object-cover" /> : <div className="mb-2 flex aspect-video items-center justify-center rounded-md bg-surface-100 text-xs text-surface-500 dark:bg-surface-800">Cena {index + 1} · imagem procedural ou ainda não criada</div>}
              {sceneImageCandidates[sourceIndex]?.image_url && <div className="mb-2 rounded-md border border-amber-400 p-2 dark:border-amber-700">
                <p className="mb-1 text-xs font-semibold text-amber-700 dark:text-amber-300">Imagem candidata · ainda não aplicada</p>
                <div className="grid grid-cols-2 gap-2">
                  <div><img src={asset?.image_url ?? visualDirections[sourceIndex]?.image_url ?? ""} alt={`Imagem atual da cena ${index + 1}`} className="aspect-video w-full rounded object-cover" /><p className="mt-1 text-center text-[10px]">Atual</p></div>
                  <div><img src={sceneImageCandidates[sourceIndex].image_url} alt={`Imagem candidata da cena ${index + 1}`} className="aspect-video w-full rounded object-cover" /><p className="mt-1 text-center text-[10px]">Candidata</p></div>
                </div>
                <button type="button" onClick={() => discardSceneImage(sourceIndex)} className="ml-2 mt-2 rounded-md border border-surface-300 px-3 py-1.5 text-xs font-semibold dark:border-surface-600">Manter imagem atual</button>
                <button type="button" onClick={() => approveSceneImage(sourceIndex)} disabled={approvingImageScene !== null} className="mt-2 rounded-md bg-emerald-600 px-3 py-1.5 text-xs font-semibold text-white disabled:opacity-40">{approvingImageScene === sourceIndex ? "Aprovando…" : "Aprovar nova imagem"}</button>
              </div>}
              <label className="mb-2 flex items-center gap-2 text-xs font-semibold text-surface-700 dark:text-surface-300">
                <input type="checkbox" checked={selectedImageScenes.includes(sourceIndex)} onChange={(event) => setSelectedImageScenes((current) => event.target.checked ? [...new Set([...current, sourceIndex])] : current.filter((value) => value !== sourceIndex))} />
                Selecionar cena {index + 1}
              </label>
              {visualDirections[sourceIndex] && <div className="mb-2 rounded-md bg-surface-50 p-2 text-[11px] dark:bg-surface-800">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="rounded-full bg-primary-100 px-2 py-0.5 font-semibold text-primary-700 dark:bg-primary-950 dark:text-primary-300">{visualDirections[sourceIndex].narrative_beat.replaceAll("_", " ")}</span>
                  <span className="text-surface-500">Plano: {visualDirections[sourceIndex].shot_type}</span>
                </div>
                {visualDirections[sourceIndex].narration && <p className="mt-1 text-surface-600 dark:text-surface-300">Narração: {visualDirections[sourceIndex].narration}</p>}
                {visualDirections[sourceIndex].visual_direction && <p className="mt-1 text-surface-500">Direção: {visualDirections[sourceIndex].visual_direction}</p>}
                {visualDirections[sourceIndex].storyboard_scene_id && <p className="mt-1 text-surface-400">ID: {visualDirections[sourceIndex].storyboard_scene_id}</p>}
                {visualDirections[sourceIndex].storyboard_status === "needs_review" && <p className="mt-1 font-semibold text-amber-600">Esta cena precisa de revisão manual: falta uma descrição visual ou narração.</p>}
                {(visualDirections[sourceIndex].continuity?.characters?.length || visualDirections[sourceIndex].continuity?.objects?.length) ? <p className="mt-1 text-surface-500">Continuidade: {[...(visualDirections[sourceIndex].continuity?.characters ?? []), ...(visualDirections[sourceIndex].continuity?.objects ?? [])].join(" · ")}</p> : null}
                {visualDirections[sourceIndex].negative_prompt && <details className="mt-1"><summary className="cursor-pointer text-surface-500">Restrições da imagem</summary><p className="mt-1 text-surface-400">{visualDirections[sourceIndex].negative_prompt}</p></details>}
              </div>}
              <label className="mb-1 block text-[10px] font-medium text-surface-500">Prompt visual · edite antes de regenerar</label>
              <textarea value={sceneImagePrompts[sourceIndex] ?? sceneImagePrompts[index] ?? visualDirections[sourceIndex]?.visual_prompt_suggestion ?? visualDirections[sourceIndex]?.visual_prompt ?? ""} onChange={(event) => setSceneImagePrompts((current) => ({ ...current, [sourceIndex]: event.target.value }))} rows={2} maxLength={4000} placeholder="Descreva o enquadramento, cenário e ação desta cena…" className="w-full rounded-md border border-surface-200 bg-transparent p-2 text-xs dark:border-surface-700" />
              <button type="button" onClick={() => editSceneImage(sourceIndex)} disabled={!(sceneImagePrompts[sourceIndex] ?? sceneImagePrompts[index] ?? visualDirections[sourceIndex]?.visual_prompt_suggestion)?.trim() || editingImageScene !== null} className="mt-2 rounded-md border border-primary-300 px-3 py-1.5 text-xs font-semibold disabled:opacity-40 dark:border-primary-700">
                {editingImageScene === sourceIndex ? "Gerando imagem…" : asset ? "Regenerar somente esta cena" : "Criar imagem desta cena"}
              </button>
              <button type="button" onClick={() => asset && generateSceneMotion(index, asset)} disabled={!asset?.image_path || generatingMotionScene !== null} className="ml-2 mt-2 rounded-md border border-violet-300 px-3 py-1.5 text-xs font-semibold disabled:opacity-40 dark:border-violet-700">
                {generatingMotionScene === index ? "Gerando vídeo IA…" : "Animar com IA · ComfyUI"}
              </button>
              {generatedMotionClips[sceneOrder[index] ?? index] && <div className="mt-2 space-y-1">
                <video controls preload="metadata" src={generatedMotionClips[sceneOrder[index] ?? index]} className="w-full rounded-md" />
                <a href={generatedMotionClips[sceneOrder[index] ?? index]} target="_blank" rel="noreferrer" className="text-xs font-medium text-primary-600 underline">Abrir clipe generativo da cena {index + 1}</a>
              </div>}
              {asset?.status === "edited" && <p className="mt-1 text-[10px] text-emerald-600">Imagem atualizada · {asset.operation === "image_to_image" ? "edição da imagem anterior" : "imagem criada do zero"}</p>}
            </div>;
          })}
        </div>
      </section>}

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
            <button type="button" onClick={analyzeVisuals} disabled={!jobId || dirty || audioDirty || saving || savingAudio || analyzingVisuals} className="rounded-md border border-primary-300 px-3 py-2 text-xs font-semibold disabled:opacity-40 dark:border-primary-700">
              {analyzingVisuals ? "Analisando visual…" : "Analisar qualidade visual"}
            </button>
            <button type="button" onClick={analyzeSceneImageSimilarity} disabled={!jobId || dirty || audioDirty || saving || savingAudio || analyzingImageSimilarity} className="rounded-md border border-primary-300 px-3 py-2 text-xs font-semibold disabled:opacity-40 dark:border-primary-700">
              {analyzingImageSimilarity ? "Comparando imagens…" : "Detectar imagens repetidas"}
            </button>
            <button type="button" onClick={analyzeMp4Visuals} disabled={!jobId || dirty || audioDirty || saving || savingAudio || analyzingMp4Visuals} className="rounded-md border border-primary-300 px-3 py-2 text-xs font-semibold disabled:opacity-40 dark:border-primary-700">
              {analyzingMp4Visuals ? "Extraindo frames…" : "Analisar MP4 renderizado"}
            </button>
            <button type="button" onClick={analyzeAvSync} disabled={!jobId || dirty || audioDirty || saving || savingAudio || analyzingAvSync} className="rounded-md border border-primary-300 px-3 py-2 text-xs font-semibold disabled:opacity-40 dark:border-primary-700">
              {analyzingAvSync ? "Verificando sincronização…" : "Verificar A/V"}
            </button>
            <button type="button" onClick={saveAudioDraft} disabled={savingAudio || dirty || saving || (!audioDirty && !musicAsset.trim() && !sfxAsset.trim())} className="rounded-md border border-surface-300 px-3 py-2 text-xs font-semibold disabled:opacity-40 dark:border-surface-600">
              {savingAudio ? "Salvando áudio…" : audioDirty ? "Salvar alterações de áudio" : "Salvar faixas de áudio"}
            </button>
            <span className="text-[11px] text-surface-400">A lista mostra arquivos gerados em music, effects, voice, dubbing e mix. Caminhos externos são bloqueados.</span>
          </div>
          {continuityReport && <div className="rounded-md border border-surface-200 p-3 text-xs dark:border-surface-700 sm:col-span-2">
            <div className="flex flex-wrap items-center justify-between gap-2"><strong>Consistência de personagens e figurinos</strong><span className={continuityReport.warnings.length ? "text-amber-600" : "text-emerald-600"}>{continuityReport.warnings.length ? continuityReport.warnings.length + " pontos para revisar" : "Metadados consistentes"}</span></div>
            <p className="mt-1 text-surface-500">{continuityReport.checked_scenes} cenas · validação {continuityReport.method}</p>
            {continuityReport.warnings.length > 0 && <ul className="mt-2 list-disc space-y-1 pl-5">{continuityReport.warnings.map((warning, index) => <li key={index}>{warning.message} Cenas: {warning.scene_indices.map((value) => value + 1).join(", ")}.</li>)}</ul>}
            <p className="mt-2 text-surface-400">A verificação atual compara metadados do storyboard; ainda não identifica automaticamente personagens nos pixels das imagens.</p>
          </div>}
          {imageSimilarityReport && <div className="rounded-md border border-surface-200 p-3 text-xs dark:border-surface-700 sm:col-span-2">
            <div className="flex flex-wrap items-center justify-between gap-2"><strong>Comparação real das imagens das cenas</strong><span className={imageSimilarityReport.duplicate_pairs.length ? "text-amber-600" : "text-emerald-600"}>{imageSimilarityReport.duplicate_pairs.length ? imageSimilarityReport.duplicate_pairs.length + " pares semelhantes" : "Nenhuma duplicata detectada"}</span></div>
            <p className="mt-1 text-surface-500">{imageSimilarityReport.image_count} imagens · {imageSimilarityReport.compared_pairs} comparações · método {imageSimilarityReport.method}</p>
            {imageSimilarityReport.duplicate_pairs.length > 0 ? <ul className="mt-2 list-disc space-y-1 pl-5">{imageSimilarityReport.duplicate_pairs.map((pair, index) => <li key={index}>Cenas {pair.scene_indices[0] + 1} e {pair.scene_indices[1] + 1}: {pair.match_type === "exact" ? "arquivos idênticos" : "possível duplicata visual"} · {pair.similarity_percent}% de similaridade estrutural</li>)}</ul> : <p className="mt-2 text-emerald-600">Nenhum par ultrapassou o limite de semelhança configurado.</p>}
            <p className="mt-2 text-surface-400">Usa SHA-256 e difference hash perceptual de 64 bits sobre os pixels. Sem reconhecimento semântico; confirme visualmente antes de excluir ou substituir imagens.</p>
          </div>}
          {mp4VisualReport && <div className="rounded-md border border-surface-200 p-3 text-xs dark:border-surface-700 sm:col-span-2">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <strong>Scene Intelligence · frames reais do MP4</strong>
              <span className={mp4VisualReport.status === "no_obvious_issue" ? "text-emerald-600" : "text-amber-600"}>{mp4VisualReport.status.replaceAll("_", " ")}</span>
            </div>
            <p className="mt-1 text-surface-500">{mp4VisualReport.sample_count} frames amostrados · intervalo {mp4VisualReport.sample_interval_seconds}s · vídeo {mp4VisualReport.video_source === "edited" ? "editado" : "original"} · {mp4VisualReport.video_duration_seconds}s</p>
            <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-4">
              <div className="rounded bg-surface-100 p-2 dark:bg-surface-800"><div className="text-surface-500">Pares repetidos</div><strong>{mp4VisualReport.duplicate_pair_count}</strong></div>
              <div className="rounded bg-surface-100 p-2 dark:bg-surface-800"><div className="text-surface-500">Pares quase estáticos</div><strong>{mp4VisualReport.low_change_pair_count}</strong></div>
              <div className="rounded bg-surface-100 p-2 dark:bg-surface-800"><div className="text-surface-500">Trechos estáticos</div><strong>{mp4VisualReport.static_runs.length}</strong></div>
              <div className="rounded bg-surface-100 p-2 dark:bg-surface-800"><div className="text-surface-500">Comparações</div><strong>{mp4VisualReport.comparison_count}</strong></div>
            </div>
            {mp4VisualReport.static_runs.length > 0 && <div className="mt-3"><strong>Trechos com pouca mudança visual</strong><ul className="mt-1 list-disc pl-5">{mp4VisualReport.static_runs.map((run, index) => <li key={index}>{run.start_seconds}s–{run.end_seconds}s ({run.comparison_count} comparações)</li>)}</ul></div>}
            {mp4VisualReport.scene_summaries.length > 0 && <div className="mt-3"><strong>Resumo por cena</strong><ul className="mt-1 space-y-1">{mp4VisualReport.scene_summaries.map((scene) => <li key={scene.scene_index}>Cena {scene.scene_index + 1}: {scene.sampled_comparisons} amostras · {scene.repeated_frame_pairs} pares repetidos · {scene.low_change_pairs} pares estáticos</li>)}</ul></div>}
            {mp4VisualReport.warnings.length > 0 && <ul className="mt-2 list-disc space-y-1 pl-5 text-amber-600">{mp4VisualReport.warnings.map((warning, index) => <li key={index}>{warning.code.replaceAll("_", " ")} · {warning.count}</li>)}</ul>}
            <p className="mt-2 text-surface-400">Análise de frames amostrados com FFmpeg, Pillow e NumPy. Não reconhece personagens nem comprova movimento semântico ou qualidade artística.</p>
          </div>}
          {visualReport && <div className="rounded-md border border-surface-200 p-3 text-xs dark:border-surface-700 sm:col-span-2">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <strong>Visual Intelligence · {visualReport.studio_id === "whymentary" ? "Whymentary" : "Documentário Histórico"}</strong>
              <span className={visualReport.status === "good" ? "text-emerald-600" : "text-amber-600"}>{visualReport.score}/100 · {visualReport.status.replaceAll("_", " ")}</span>
            </div>
            <p className="mt-1 text-surface-500">{visualReport.scene_count} cenas · {visualReport.moving_camera_scenes} com movimento de câmera · {visualReport.animated_primitives} elementos animados · {visualReport.unique_shot_types} tipos de plano</p>
            <p className="mt-1 text-surface-500">Transições: {Object.entries(visualReport.transition_counts).map(([type, count]) => `${type} ${count}`).join(" · ") || "não especificadas"}</p>
            <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-4">
              {Object.entries(visualReport.components).map(([key, value]) => <div key={key} className="rounded bg-surface-100 p-2 dark:bg-surface-800"><div className="capitalize text-surface-500">{key === "motion" ? "Movimento" : key === "composition" ? "Composição" : key === "variety" ? "Variedade" : "Clareza"}</div><strong>{value}/100</strong></div>)}
            </div>
            {visualReport.warnings.length > 0 ? <ul className="mt-3 list-disc space-y-1 pl-5 text-amber-600">{visualReport.warnings.map((warning, index) => <li key={index}>{warning.code.replaceAll("_", " ")}{typeof warning.scene_index === "number" ? ` · cena ${warning.scene_index + 1}` : ""}</li>)}</ul> : <p className="mt-2 text-emerald-600">Nenhum alerta nos metadados avaliados.</p>}
            <p className="mt-2 text-surface-400">Pontuação heurística dos descritores da cena; não é análise de pixels do MP4. Revise o vídeo antes da publicação.</p>
          </div>}
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
        {vidGridRecoveryPlan && <p className="mb-2 text-xs text-surface-500">
          Recuperação inteligente: {vidGridRecoveryPlan.ready_count}/{vidGridRecoveryPlan.scene_count} cenas prontas
          {vidGridRecoveryPlan.blocked_count > 0 && ` · ${vidGridRecoveryPlan.blocked_count} sem imagem válida`}
        </p>}
        {jobId && staleVidGridClipCount > 0 && <button
          type="button"
          onClick={rebuildStaleVidGridClips}
          disabled={rebuildingVidGridClips || rendering || previewing || saving || dirty || audioDirty || savingAudio}
          className="rounded-md border border-amber-300 px-3 py-2 text-xs font-semibold text-amber-700 disabled:opacity-40 dark:border-amber-700 dark:text-amber-300"
          title="Reconstrói apenas cenas com clipe ausente, inválido, desatualizado ou incompatível com a imagem aprovada e o perfil atual."
        >
          {rebuildingVidGridClips ? "Reconstruindo clipes…" : `Recuperar ${staleVidGridClipCount} cena(s) VidGrid`}
        </button>}
        {jobId && <>
          <button type="button" onClick={saveDraft} disabled={saving || !dirty || audioDirty} className="rounded-md border border-surface-300 px-3 py-2 text-xs font-semibold disabled:opacity-40 dark:border-surface-600">
            {saving ? "Salvando…" : "Salvar rascunho"}
          </button>
          <button type="button" onClick={previewEdits} disabled={previewing || rendering || saving || dirty || audioDirty || savingAudio} className="rounded-md border border-violet-300 px-3 py-2 text-xs font-semibold disabled:opacity-40 dark:border-violet-700">
            {previewing ? "Gerando prévia…" : "Pré-visualizar montagem"}
          </button>
          <button type="button" onClick={renderEdits} disabled={rendering || previewing || saving || dirty || audioDirty || savingAudio} className="rounded-md bg-primary-600 px-3 py-2 text-xs font-semibold text-white disabled:opacity-40">
            {rendering ? "Renderizando MP4…" : "Renderizar edição"}
          </button>
        </>}
      </div>
      {message && <p role="status" className="mt-2 text-xs text-surface-500">{message}</p>}
      {renderUrl && <p className="mt-2 text-xs"><a className="text-primary-600 underline" href={renderUrl} target="_blank" rel="noreferrer">Abrir MP4 renderizado</a></p>}
      {renderUrl && <button type="button" onClick={validateOutput} className="mt-2 rounded border px-3 py-2 text-xs">Validar MP4 final</button>}
      {jobId && <button type="button" onClick={checkAssetHealth} disabled={checkingAssetHealth || rendering || rebuildingVidGridClips} className="mt-2 ml-2 rounded border px-3 py-2 text-xs disabled:opacity-40">
        {checkingAssetHealth ? "Auditando ativos…" : "Auditar saúde dos ativos"}
      </button>}
      {jobId && <button type="button" onClick={loadDependencyGraph} disabled={loadingDependencyGraph || rendering || rebuildingVidGridClips} className="mt-2 ml-2 rounded border px-3 py-2 text-xs disabled:opacity-40">
        {loadingDependencyGraph ? "Mapeando dependências…" : "Mapa de dependências"}
      </button>}
      {dependencyGraph && <div className="mt-3 rounded-md border border-surface-200 p-3 text-xs dark:border-surface-700" aria-label="Mapa de dependências do projeto">
        <strong>Dependências da produção</strong>
        <div className="mt-2 flex flex-wrap gap-3">
          <span>Ativos: <strong>{dependencyGraph.summary.nodes}</strong></span>
          <span>Relações: <strong>{dependencyGraph.summary.dependencies}</strong></span>
          <span>Ausentes: <strong>{dependencyGraph.summary.statuses.missing ?? 0}</strong></span>
          <span>Corrompidos: <strong>{dependencyGraph.summary.statuses.corrupt ?? 0}</strong></span>
        </div>
        <ul className="mt-2 grid gap-1 sm:grid-cols-2">
          {dependencyGraph.impact_rules.map((rule) => <li key={rule.changed} className="rounded bg-surface-50 p-2 dark:bg-surface-800">
            <strong>{rule.changed}</strong> → {rule.rebuild.join(" + ")}
            {rule.condition ? <span className="block text-surface-500">{rule.condition}</span> : null}
          </li>)}
        </ul>
        <p className="mt-2 text-[10px] text-surface-500">Mapa baseado nas referências persistidas. A reconstrução ainda exige ação explícita e não ocorre automaticamente.</p>
      </div>}
      {assetHealth && <div className="mt-3 rounded-md border border-surface-200 p-3 text-xs dark:border-surface-700" aria-label="Saúde dos ativos do projeto">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <strong>Saúde dos ativos</strong>
          <span className={assetHealth.status === "healthy" ? "font-semibold text-emerald-600" : "font-semibold text-amber-600"}>
            {assetHealth.status === "healthy" ? "Todos os ativos disponíveis" : "Atenção necessária"}
          </span>
        </div>
        <div className="mt-2 grid grid-cols-2 gap-2 sm:grid-cols-5">
          <span>Total: <strong>{assetHealth.summary.total_assets}</strong></span>
          <span>Disponíveis: <strong>{assetHealth.summary.available}</strong></span>
          <span>Ausentes: <strong>{assetHealth.summary.missing}</strong></span>
          <span>Corrompidos: <strong>{assetHealth.summary.corrupt}</strong></span>
          <span>Ilegíveis: <strong>{assetHealth.summary.unreadable}</strong></span>
        </div>
        {!!assetHealth.scenes.filter((scene) => scene.status !== "healthy").length && <ul className="mt-2 list-disc pl-5">
          {assetHealth.scenes.filter((scene) => scene.status !== "healthy").map((scene, index) => <li key={index}>
            {scene.scene_index !== undefined ? `Cena ${scene.scene_index + 1}` : scene.group ?? "Áudio"}: {scene.assets.filter((asset) => asset.status !== "available").map((asset) => asset.kind + " (" + asset.status + ")").join(", ")}
          </li>)}
        </ul>}
        <p className="mt-2 text-[10px] text-surface-500">Verificação de existência, leitura básica e SHA-256. Não é análise semântica nem validação perceptual de sincronização.</p>
      </div>}
      {outputValidation && <p className="mt-2 text-xs">Integridade: {outputValidation.integrity ?? "—"} · {outputValidation.resolution ?? "resolução não lida"} · {outputValidation.fps ?? "FPS não lido"} · vídeo: {outputValidation.video_codec ?? "—"} · áudio: {outputValidation.audio?.codec_name ?? "—"} · alertas: {outputValidation.warnings.length} · erros: {outputValidation.errors.length}</p>}
      {previewUrl && <div className="mt-3 max-w-3xl rounded-lg border border-violet-200 p-3 dark:border-violet-800">
        <div className="mb-2 flex flex-wrap items-center justify-between gap-2 text-xs">
          <strong>Prévia visual da montagem</strong>
          <a className="text-primary-600 underline" href={previewUrl} target="_blank" rel="noreferrer">Abrir prévia</a>
        </div>
        <video src={previewUrl} controls preload="metadata" className="max-h-[520px] w-full rounded-md bg-black" />
        <p className="mt-2 text-[11px] text-surface-500">Proxy de baixa resolução para revisar ordem, imagens e transições. A mixagem de áudio e as legendas devem ser conferidas no MP4 final.</p>
      </div>}

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
