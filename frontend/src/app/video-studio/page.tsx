"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { DashboardLayout } from "@/components/DashboardLayout";
import { Card, CardHeader, CardBody } from "@/components/cards/Card";
import { Badge } from "@/components/badges/Badge";
import { Button } from "@/components/buttons/Button";
import { useAuthStore } from "@/stores/authStore";
import { videoStudioApi, type StudioJob, type StudioVoice, type StudioProfile, type StudioCharacter, type StudioSceneObject } from "@/api/videoStudio";
import { extractErrorMessage } from "@/utils/apiError";
import EditTimelinePanel from "@/components/video-studio/EditTimelinePanel";
import { fmtBytes, fmtDuration, fmtEstimate, jobStatusVariant, studioHealthVariant } from "@/utils/format";
import {
  DURATION_PRESETS,
  FORMAT_PRESETS,
  FPS_PRESETS,
  MAX_DURATION_SECONDS,
  RESOLUTION_PRESETS,
  estimateRenderSeconds,
  formatLabel,
  formatPresetFor,
  parseResolutionPixels,
  recommendedDurationFor,
  resolutionLabel,
} from "@/utils/videoFormats";

// ---------------------------------------------------------------------------
// Real modules already implemented in modules/ai_video_studio/
// ---------------------------------------------------------------------------

const studioModules = [
  { name: "Text to Video", icon: "🎬", desc: "Prompt → MP4 com narração", status: "ready" as const, endpoint: "/api/v1/video-studio/videos/generate", color: "bg-violet-50 text-violet-600 dark:bg-violet-950 dark:text-violet-400" },
  { name: "Image to Video", icon: "🖼️", desc: "Anima imagens em vídeo", status: "ready" as const, endpoint: "/api/v1/video-studio/videos/image-to-video", color: "bg-blue-50 text-blue-600 dark:bg-blue-950 dark:text-blue-400" },
  { name: "Video to Video", icon: "🔄", desc: "Estilo, upscale, denoise", status: "ready" as const, endpoint: "/api/v1/video-studio/videos/video-to-video", color: "bg-cyan-50 text-cyan-600 dark:bg-cyan-950 dark:text-cyan-400" },
  { name: "AI Image Generator", icon: "🎨", desc: "14 estilos de imagem", status: "ready" as const, endpoint: "/api/v1/video-studio/images/generate", color: "bg-pink-50 text-pink-600 dark:bg-pink-950 dark:text-pink-400" },
  { name: "AI Voice Studio", icon: "🗣️", desc: "TTS, clones e dublagem", status: "ready" as const, endpoint: "/api/v1/video-studio/audio/synthesize", color: "bg-amber-50 text-amber-600 dark:bg-amber-950 dark:text-amber-400" },
  { name: "AI Animation", icon: "🤸", desc: "Personagens e rigging", status: "ready" as const, endpoint: "/api/v1/video-studio/animations/generate", color: "bg-emerald-50 text-emerald-600 dark:bg-emerald-950 dark:text-emerald-400" },
  { name: "AI Physics", icon: "🌊", desc: "Partículas e simulação", status: "ready" as const, endpoint: "/api/v1/video-studio/physics/simulate", color: "bg-teal-50 text-teal-600 dark:bg-teal-950 dark:text-teal-400" },
  { name: "AI Music", icon: "🎵", desc: "20 gêneros + instrumentos", status: "ready" as const, endpoint: "/api/v1/video-studio/assets/generate", color: "bg-indigo-50 text-indigo-600 dark:bg-indigo-950 dark:text-indigo-400" },
  { name: "AI Sound Effects", icon: "🌩️", desc: "16 efeitos realistas", status: "ready" as const, endpoint: "/api/v1/video-studio/assets/generate", color: "bg-sky-50 text-sky-600 dark:bg-sky-950 dark:text-sky-400" },
  { name: "AI Subtitles", icon: "💬", desc: "SRT / VTT / ASS", status: "ready" as const, endpoint: "/api/v1/video-studio/subtitles", color: "bg-rose-50 text-rose-600 dark:bg-rose-950 dark:text-rose-400" },
];

// Modules planned for future volumes — shown as "Em breve" (the 6 missing ones)
const plannedModules = [
  { name: "AI Avatar Engine", icon: "🧑‍🚀", desc: "Avatares 3D realistas" },
  { name: "AI Render Farm", icon: "🖥️", desc: "Renderização distribuída" },
  { name: "AI Video Analytics", icon: "📊", desc: "Análise de cena e métricas" },
  { name: "AI Speech Analytics", icon: "🎙️", desc: "Transcrição e insights" },
  { name: "AI Dubbing Automático", icon: "🌐", desc: "Dublagem em massa" },
  { name: "AI Streaming Engine", icon: "📡", desc: "Geração ao vivo" },
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

// Max polling ticks before giving up (1.5s each → ~3 min safety cap).
const MAX_POLL_TICKS = 120;

export default function VideoStudioPage() {
  const { user } = useAuthStore();
  const projectId = user?.id ?? "default";
  const [health, setHealth] = useState<string>("checking");
  const [version, setVersion] = useState<string>("");
  const [voices, setVoices] = useState<StudioVoice[]>([]);
  const [jobs, setJobs] = useState<StudioJob[]>([]);
  const [activeTimelineJobId, setActiveTimelineJobId] = useState<string | null>(null);
  const [studioProfiles, setStudioProfiles] = useState<StudioProfile[]>([]);
  const [studioId, setStudioId] = useState<StudioProfile["id"]>("whymentary");
  const [studioLoadError, setStudioLoadError] = useState<string | null>(null);
  const [characters, setCharacters] = useState<StudioCharacter[]>([]);
  const [selectedCharacterIds, setSelectedCharacterIds] = useState<string[]>([]);
  const [characterLoadError, setCharacterLoadError] = useState<string | null>(null);
  const [sceneObjects, setSceneObjects] = useState<StudioSceneObject[]>([]);
  const [selectedObjectIds, setSelectedObjectIds] = useState<string[]>([]);
  const [sceneImageMode, setSceneImageMode] = useState<"procedural" | "ai" | "auto">("procedural");
  const [objectLoadError, setObjectLoadError] = useState<string | null>(null);

  // Generation form state
  const [prompt, setPrompt] = useState("A cinematic drone shot over a misty mountain range at sunrise, with a voiceover narration");
  const [voiceover, setVoiceover] = useState(true);
  const [generateSubtitles, setGenerateSubtitles] = useState(false);
  const [voiceId, setVoiceId] = useState("default");
  const [mode, setMode] = useState<"per_scene" | "single">("per_scene");
  const [numScenes, setNumScenes] = useState(3);
  const [vidgridCompatible, setVidgridCompatible] = useState(true);
  const [duration, setDuration] = useState(6);
  const effectiveDuration = vidgridCompatible ? numScenes * 10 : duration;
  const [resolution, setResolution] = useState<string>(RESOLUTION_PRESETS[0].value);
  const [frameRate, setFrameRate] = useState<number>(FPS_PRESETS[0]);
  // Active platform format preset ("custom" once the user tweaks any dimension).
  const [format, setFormat] = useState<string>("custom");
  const [generating, setGenerating] = useState(false);
  const [generationError, setGenerationError] = useState<string | null>(null);
  const pollTimer = useRef<ReturnType<typeof setInterval> | null>(null);

  // Estimated render time for the current resolution/fps/duration combo.
  const estimatedSeconds = estimateRenderSeconds(effectiveDuration, frameRate, parseResolutionPixels(resolution));
  const isLongVideo = estimatedSeconds >= 180 || effectiveDuration >= 300;
  // Active platform format (if any) and the duration it recommends, used to
  // highlight the matching DURATION_PRESETS chip.
  const activeFormat = formatPresetFor(format);
  const recommendedDuration = recommendedDurationFor(format);

  const refreshJobs = useCallback(async () => {
    try {
      setJobs(await videoStudioApi.listJobs());
    } catch {
      // Backend may be offline — keep last known jobs.
    }
  }, []);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const h = await videoStudioApi.health();
        if (!cancelled) {
          setHealth(h.status);
          setVersion(h.version);
        }
      } catch {
        if (!cancelled) setHealth("offline");
      }
      try {
        const profiles = await videoStudioApi.listStudios();
        if (!cancelled) setStudioProfiles(profiles);
      } catch (e) {
        if (!cancelled) setStudioLoadError(extractErrorMessage(e, "Não foi possível carregar os estúdios"));
      }
      try {
        const v = await videoStudioApi.listVoices();
        if (!cancelled && v.length) setVoices(v);
      } catch {
        // voices optional
      }
      await refreshJobs();
    })();
    return () => {
      cancelled = true;
      if (pollTimer.current) clearInterval(pollTimer.current);
    };
  }, [refreshJobs]);

  useEffect(() => {
    let cancelled = false;
    setSelectedCharacterIds([]);
    setSelectedObjectIds([]);
    videoStudioApi.listSceneObjects(studioId).then((items) => {
      if (!cancelled) { setSceneObjects(items); setObjectLoadError(null); }
    }).catch((error) => {
      if (!cancelled) { setSceneObjects([]); setObjectLoadError(extractErrorMessage(error, "Não foi possível carregar os objetos")); }
    });
    videoStudioApi.listCharacters(studioId).then((items) => {
      if (!cancelled) {
        setCharacters(items);
        setCharacterLoadError(null);
      }
    }).catch((error) => {
      if (!cancelled) {
        setCharacters([]);
        setCharacterLoadError(extractErrorMessage(error, "Não foi possível carregar os personagens"));
      }
    });
    return () => { cancelled = true; };
  }, [studioId]);

  const pollUntilDone = useCallback(async (jobId: string) => {
    if (pollTimer.current) clearInterval(pollTimer.current);
    let ticks = 0;
    pollTimer.current = setInterval(async () => {
      ticks += 1;
      if (ticks >= MAX_POLL_TICKS) {
        if (pollTimer.current) clearInterval(pollTimer.current);
        return;
      }
      try {
        const job = await videoStudioApi.getJob(jobId);
        setJobs((prev) => prev.map((j) => (j.job_id === jobId ? job : j)));
        if (job.status === "completed" || job.status === "failed") {
          if (pollTimer.current) clearInterval(pollTimer.current);
        }
      } catch {
        if (pollTimer.current) clearInterval(pollTimer.current);
      }
    }, 1500);
  }, []);

  // Scale the scene count with the duration so longer videos don't stretch
  // a handful of scenes (target ~1 scene per 20s, clamped to the API range).
  const suggestedScenesFor = (seconds: number) =>
    Math.min(20, Math.max(3, Math.round(seconds / 20)));

  const applyDurationPreset = (seconds: number) => {
    setFormat("custom");
    setDuration(seconds);
    setNumScenes(suggestedScenesFor(seconds));
  };

  const applyFormatPreset = (preset: (typeof FORMAT_PRESETS)[number]) => {
    setFormat(preset.value);
    setResolution(preset.resolution);
    setFrameRate(preset.fps);
    setDuration(preset.duration);
    setNumScenes(suggestedScenesFor(preset.duration));
  };

  const handleGenerate = async () => {
    setGenerating(true);
    setGenerationError(null);
    try {
      const job = await videoStudioApi.generateVideo({
        project_id: projectId,
        prompt,
        studio_id: studioId,
        character_ids: selectedCharacterIds,
        object_ids: selectedObjectIds,
        scene_image_mode: sceneImageMode,
        voiceover,
        generate_subtitles: generateSubtitles,
        voice_id: voiceId,
        voiceover_mode: mode,
        num_scenes: Math.min(20, Math.max(1, numScenes)),
        duration_seconds: Math.min(MAX_DURATION_SECONDS, Math.max(1, effectiveDuration)),
        vidgrid_compatible: vidgridCompatible,
        resolution,
        frame_rate: frameRate,
        llm_timeout: 60,
        format,
      });
      setJobs((prev) => [job, ...prev]);
      pollUntilDone(job.job_id);
    } catch (e) {
      // Surface the backend's real message (e.g. the 422 reason for an
      // unsupported resolution aspect ratio) instead of a generic fetch error.
      setGenerationError(extractErrorMessage(e, "Falha ao gerar vídeo"));
    } finally {
      setGenerating(false);
    }
  };

  // Health label/dot config (variants live in format.ts via `studioHealthVariant`).
  const healthBadgeMap = {
    checking: { label: "Verificando…", dot: false },
    healthy: { label: "Backend conectado", dot: true },
    offline: { label: "Backend offline", dot: true },
  };
  const healthBadge = healthBadgeMap[health as keyof typeof healthBadgeMap] ?? healthBadgeMap.checking;

  const readyCount = studioModules.length;
  const totalCount = readyCount + plannedModules.length;

  return (
    <DashboardLayout>
      {/* ─── Header ──────────────────────────────────────────────────── */}
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500 to-fuchsia-600 text-2xl shadow-lg">
            🎬
          </div>
          <div>
            <h1 className="text-2xl font-bold text-surface-900 dark:text-surface-50">
              AI Video Studio
            </h1>
            <p className="mt-0.5 text-sm text-surface-500">
              Suite completa de geração de vídeo, voz e mídia — {readyCount}/{totalCount} módulos
              {version ? ` · v${version}` : ""}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant={studioHealthVariant(health)} size="md" dot={healthBadge.dot}>
            {healthBadge.label}
          </Badge>
          <Button variant="secondary" size="sm" onClick={() => window.open("/docs", "_blank")}>
            📚 API Docs
          </Button>
        </div>
      </div>

      {/* ─── Generation Panel ────────────────────────────────────────── */}
      <Card className="mb-8">
        <CardHeader>
          <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
            Gerar vídeo com narração
          </h2>
          <Badge variant="primary" size="sm">Text to Video + TTS</Badge>
        </CardHeader>
        <CardBody>
          <section className="mb-5 rounded-xl border border-surface-200 bg-surface-50 p-4 dark:border-surface-700 dark:bg-surface-900/50" aria-labelledby="darkstudio-profile-title">
            <div className="mb-3">
              <h3 id="darkstudio-profile-title" className="text-sm font-semibold text-surface-900 dark:text-surface-100">DARKSTUDIO AI · Escolha seu estúdio</h3>
              <p className="mt-1 text-xs text-surface-500">O perfil selecionado define a linguagem visual aplicada durante a renderização.</p>
            </div>
            <div className="grid gap-3 md:grid-cols-2">
              {[{ id: "whymentary" as const, title: "Whymentary", subtitle: "Explicações 2D · fundo branco · cores chapadas", mark: "✍️" }, { id: "historical_documentary" as const, title: "Documentário Histórico", subtitle: "Ilustração cinematográfica · profundidade · luz dramática", mark: "🏛️" }].map((profile) => {
                const active = studioId === profile.id;
                return (
                  <button key={profile.id} type="button" aria-pressed={active} onClick={() => setStudioId(profile.id)} className={active ? "rounded-lg border border-primary-500 bg-primary-50 p-3 text-left ring-2 ring-primary-500/20 dark:bg-primary-950/30" : "rounded-lg border border-surface-200 bg-white p-3 text-left hover:border-primary-300 dark:border-surface-700 dark:bg-surface-800"}>
                    <span className="flex items-center gap-2 text-sm font-semibold text-surface-900 dark:text-surface-100"><span aria-hidden="true">{profile.mark}</span>{profile.title}{active && <span className="ml-auto text-xs text-primary-600 dark:text-primary-300">Selecionado</span>}</span>
                    <span className="mt-1 block text-xs text-surface-500">{profile.subtitle}</span>
                  </button>
                );
              })}
            </div>
            {studioLoadError && <p role="status" className="mt-2 text-xs text-amber-600">{studioLoadError} · seleção local disponível.</p>}
            {studioProfiles.length > 0 && <p className="mt-2 text-xs text-surface-400">{studioProfiles.length} perfis carregados da API.</p>}
          </section>
          <section className="mb-5 rounded-xl border border-surface-200 p-4 dark:border-surface-700" aria-labelledby="darkstudio-characters-title">
            <div className="mb-3">
              <h3 id="darkstudio-characters-title" className="text-sm font-semibold text-surface-900 dark:text-surface-100">Personagens recorrentes</h3>
              <p className="mt-1 text-xs text-surface-500">Os personagens selecionados aparecem nas cenas com identidade visual consistente.</p>
            </div>
            {characters.length > 0 ? (
              <div className="grid gap-2 sm:grid-cols-2">
                {characters.map((character) => {
                  const checked = selectedCharacterIds.includes(character.id);
                  const disabled = !checked && selectedCharacterIds.length >= 2;
                  return (
                    <label key={character.id} className="flex cursor-pointer items-start gap-3 rounded-lg border border-surface-200 p-3 dark:border-surface-700">
                      <input type="checkbox" checked={checked} disabled={disabled}
                        onChange={(event) => setSelectedCharacterIds((current) =>
                          event.target.checked ? [...current, character.id] : current.filter((id) => id !== character.id)
                        )}
                        className="mt-1 h-4 w-4 accent-primary-600" />
                      <span>
                        <span className="block text-sm font-medium text-surface-800 dark:text-surface-100">{character.name}</span>
                        <span className="block text-xs text-surface-500">{character.appearance.outfit ?? character.appearance.clothing_color ?? "Personagem do estúdio"}</span>
                      </span>
                    </label>
                  );
                })}
              </div>
            ) : (
              <p className="text-xs text-surface-500">{characterLoadError ?? "Carregando personagens do estúdio…"}</p>
            )}
            <p className="mt-2 text-xs text-surface-400">Até 2 personagens por vídeo. A seleção é opcional.</p>
          </section>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            rows={3}
            className="w-full rounded-lg border border-surface-300 bg-white px-3 py-2 text-sm text-surface-900 outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 dark:border-surface-600 dark:bg-surface-800 dark:text-surface-100"
            placeholder="Descreva a cena do vídeo…"
          />

          {/* ── Platform format presets ──────────────────────────── */}
          <div>
            <p className="mb-2 text-xs font-medium text-surface-500">
              📐 Formato (ajusta duração, resolução e fps juntos)
            </p>
            <div className="flex flex-wrap gap-2">
              {FORMAT_PRESETS.map((preset) => {
                const active = format === preset.value;
                return (
                  <button
                    key={preset.value}
                    type="button"
                    aria-pressed={active}
                    onClick={() => applyFormatPreset(preset)}
                    className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium transition-all ${
                      active
                        ? "bg-primary-600 text-white shadow-sm"
                        : "bg-surface-100 text-surface-700 hover:bg-surface-200 dark:bg-surface-800 dark:text-surface-300 dark:hover:bg-surface-700"
                    }`}
                  >
                    <span>{preset.icon}</span>
                    <span>{preset.label}</span>
                    <span className={`text-[10px] ${active ? "text-white/80" : "text-surface-400"}`}>
                      {preset.hint}
                    </span>
                  </button>
                );
              })}
            </div>
            {format !== "custom" && (
              <p className="mt-2 text-xs text-surface-400">
                Formato ativo: {FORMAT_PRESETS.find((p) => p.value === format)?.label} · alterações manuais em duração/resolução/fps voltam para &quot;personalizado&quot;
              </p>
            )}
          </div>

          <label className="flex items-start gap-3 rounded-xl border border-primary-200 bg-primary-50/50 p-3 dark:border-primary-900 dark:bg-primary-950/20">
            <input type="checkbox" checked={vidgridCompatible} onChange={(event) => setVidgridCompatible(event.target.checked)} className="mt-0.5 h-4 w-4 accent-primary-600" />
            <span>
              <span className="block text-sm font-semibold text-surface-900 dark:text-surface-100">Modo compatível com VidGrid — clipes de 10 segundos</span>
              <span className="mt-1 block text-xs text-surface-500">Cada cena será gerada com exatamente 10 segundos. Com {numScenes} cenas, o vídeo terá {numScenes * 10} segundos no total.</span>
            </span>
          </label>

          {/* ── Duration presets ─────────────────────────────────── */}
          <div>
            <p className="mb-2 text-xs font-medium text-surface-500">
              ⏱️ Duração livre do vídeo {vidgridCompatible ? "(desative o modo VidGrid para editar)" : ""}
            </p>
            <div className="flex flex-wrap gap-2">
              {DURATION_PRESETS.map((preset) => {
                const active = duration === preset.seconds;
                const suggested = recommendedDuration === preset.seconds;
                return (
                  <button
                    key={preset.seconds}
                    type="button"
                    disabled={vidgridCompatible}
                    aria-pressed={active}
                    title={suggested ? `${preset.label} — recomendado para ${activeFormat?.label}` : undefined}
                    onClick={() => applyDurationPreset(preset.seconds)}
                    className={`relative rounded-lg px-3 py-1.5 text-sm font-medium transition-all ${
                      active
                        ? "bg-primary-600 text-white shadow-sm"
                        : suggested
                          ? "bg-primary-50 text-primary-700 ring-2 ring-primary-400/70 hover:bg-primary-100 dark:bg-primary-950/50 dark:text-primary-300 dark:ring-primary-600"
                          : "bg-surface-100 text-surface-700 hover:bg-surface-200 dark:bg-surface-800 dark:text-surface-300 dark:hover:bg-surface-700"
                    }`}
                  >
                    {preset.label}
                    {suggested && (
                      <span className="absolute -right-1.5 -top-1.5 text-[10px]" aria-hidden="true">✦</span>
                    )}
                  </button>
                );
              })}
            </div>
            <p className="mt-2 text-xs text-surface-400">
              Atual: <span className="font-semibold text-surface-600 dark:text-surface-300">{fmtDuration(effectiveDuration)}</span> · {vidgridCompatible ? "10s por cena" : "limite de 10 minutos"}
            </p>
            {vidgridCompatible && <p className="mt-1 text-xs text-surface-400">Os presets ficam visíveis como referência, mas a duração é calculada automaticamente em blocos de 10 segundos.</p>}
            {activeFormat && recommendedDuration != null && (
              <p className="mt-1 text-xs font-medium text-primary-600 dark:text-primary-400">
                ✨ {activeFormat.label} sugere {fmtDuration(recommendedDuration)} — preset de duração destacado acima
              </p>
            )}
          </div>

          <section className="rounded-xl border border-surface-200 p-4 dark:border-surface-700" aria-labelledby="scene-object-library-title">
            <div className="mb-3 flex items-center justify-between gap-3">
              <div>
                <h3 id="scene-object-library-title" className="text-sm font-semibold text-surface-900 dark:text-surface-100">Objetos e elementos de cena</h3>
                <p className="mt-1 text-xs text-surface-500">Até seis objetos editáveis serão inseridos automaticamente em cada cena.</p>
              </div>
              <span className="text-xs tabular-nums text-surface-400">{selectedObjectIds.length}/6</span>
            </div>
            {objectLoadError && <p className="mb-2 text-xs text-amber-600">{objectLoadError}</p>}
            <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
              {sceneObjects.map((item) => {
                const checked = selectedObjectIds.includes(item.id);
                return (
                  <label key={item.id} className="flex cursor-pointer items-start gap-2 rounded-lg border border-surface-200 p-3 text-sm dark:border-surface-700">
                    <input type="checkbox" checked={checked} disabled={!checked && selectedObjectIds.length >= 6} onChange={(event) => setSelectedObjectIds((current) => event.target.checked ? [...current, item.id] : current.filter((id) => id !== item.id))} className="mt-0.5 h-4 w-4 accent-primary-600" />
                    <span className="min-w-0"><span className="block font-medium text-surface-800 dark:text-surface-200">{item.name}</span><span className="block text-xs text-surface-400">{item.description}</span></span>
                  </label>
                );
              })}
            </div>
            {!sceneObjects.length && !objectLoadError && <p className="text-xs text-surface-400">Nenhum objeto cadastrado para este estúdio.</p>}
          </section>

          <section className="rounded-xl border border-surface-200 p-4 dark:border-surface-700" aria-labelledby="scene-image-mode-title">
            <h3 id="scene-image-mode-title" className="text-sm font-semibold text-surface-900 dark:text-surface-100">Imagens das cenas</h3>
            <p className="mt-1 text-xs text-surface-500">Cada cena pode receber uma imagem própria criada a partir do texto do roteiro. Você não fica limitado à biblioteca de Mia, Leo ou objetos prontos.</p>
            <label className="mt-3 block">
              <span className="text-xs font-medium text-surface-500">Motor visual</span>
              <select value={sceneImageMode} onChange={(event) => setSceneImageMode(event.target.value as "procedural" | "ai" | "auto")} className="mt-1 w-full rounded-lg border border-surface-200 bg-transparent p-2 text-sm text-surface-900 dark:border-surface-700 dark:text-surface-100">
                <option value="procedural">Procedural — sem modelo de imagem</option>
                <option value="ai">IA local — gerar uma imagem por cena</option>
                <option value="auto">Automático — IA local e fallback procedural</option>
              </select>
            </label>
            <p className="mt-2 text-xs text-surface-400">A opção IA exige um servidor local compatível com Stable Diffusion WebUI API configurado em DARKSTUDIO_IMAGE_API_URL. O modo procedural continua disponível sem esse servidor.</p>
          </section>

          {/* ── Resolution + FPS ─────────────────────────────────── */}
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <p className="mb-2 text-xs font-medium text-surface-500">🖥️ Resolução</p>
              <div className="flex flex-wrap gap-2">
                {RESOLUTION_PRESETS.map((preset) => {
                  const active = resolution === preset.value;
                  return (
                    <button
                      key={preset.value}
                      type="button"
                      aria-pressed={active}
                      onClick={() => {
                        setResolution(preset.value);
                        setFormat("custom");
                      }}
                      className={`rounded-lg px-3 py-1.5 text-sm font-medium transition-all ${
                        active
                          ? "bg-primary-600 text-white shadow-sm"
                          : "bg-surface-100 text-surface-700 hover:bg-surface-200 dark:bg-surface-800 dark:text-surface-300 dark:hover:bg-surface-700"
                      }`}
                    >
                      {preset.label}
                    </button>
                  );
                })}
              </div>
            </div>

            <div>
              <p className="mb-2 text-xs font-medium text-surface-500">🎞️ FPS</p>
              <div className="flex flex-wrap gap-2">
                {FPS_PRESETS.map((fps) => {
                  const active = frameRate === fps;
                  return (
                    <button
                      key={fps}
                      type="button"
                      aria-pressed={active}
                      onClick={() => {
                        setFrameRate(fps);
                        setFormat("custom");
                      }}
                      className={`rounded-lg px-3 py-1.5 text-sm font-medium transition-all ${
                        active
                          ? "bg-primary-600 text-white shadow-sm"
                          : "bg-surface-100 text-surface-700 hover:bg-surface-200 dark:bg-surface-800 dark:text-surface-300 dark:hover:bg-surface-700"
                      }`}
                    >
                      {fps}fps
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          {/* ── Estimated render time warning ────────────────────── */}
          <div
            className={`rounded-lg border px-3 py-2.5 text-sm ${
              isLongVideo
                ? "border-amber-200 bg-amber-50 text-amber-800 dark:border-amber-900/60 dark:bg-amber-950/40 dark:text-amber-300"
                : "border-surface-200 bg-surface-50 text-surface-600 dark:border-surface-700 dark:bg-surface-800/50 dark:text-surface-400"
            }`}
          >
            <span className="font-medium">⏳ Tempo estimado de render: {fmtEstimate(estimatedSeconds)}</span>
            {isLongVideo && (
              <span className="ml-1">— vídeo longo pode levar vários minutos. A geração roda em background; você pode fechar esta página e voltar depois.</span>
            )}
            <span className="block text-xs opacity-70 mt-0.5">
              {effectiveDuration}s × {frameRate}fps × {resolutionLabel(resolution)} = {Math.round(effectiveDuration * frameRate).toLocaleString("pt-BR")} frames
            </span>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <label className="flex items-center gap-2 rounded-lg border border-surface-200 p-3 dark:border-surface-700">
              <input type="checkbox" checked={voiceover} onChange={(e) => setVoiceover(e.target.checked)} className="h-4 w-4 accent-primary-600" />
              <span className="text-sm text-surface-700 dark:text-surface-300">🎙️ Narração</span>
            </label>
            <label className="flex items-center gap-2 rounded-lg border border-surface-200 p-3 dark:border-surface-700">
              <input type="checkbox" checked={generateSubtitles} onChange={(e) => setGenerateSubtitles(e.target.checked)} className="h-4 w-4 accent-primary-600" />
              <span className="text-sm text-surface-700 dark:text-surface-300">💬 Gerar legendas SRT</span>
            </label>

            <label className="block rounded-lg border border-surface-200 p-3 dark:border-surface-700">
              <span className="text-xs text-surface-500">Voz</span>
              <select value={voiceId} onChange={(e) => setVoiceId(e.target.value)} className="mt-1 w-full bg-transparent text-sm text-surface-900 outline-none dark:text-surface-100">
                <option value="default">Default</option>
                {voices.map((v) => (
                  <option key={v.id} value={v.id}>{v.name}</option>
                ))}
              </select>
            </label>

            <label className="block rounded-lg border border-surface-200 p-3 dark:border-surface-700">
              <span className="text-xs text-surface-500">Modo</span>
              <select value={mode} onChange={(e) => setMode(e.target.value as "per_scene" | "single")} className="mt-1 w-full bg-transparent text-sm text-surface-900 outline-none dark:text-surface-100">
                <option value="per_scene">Por cena (sync)</option>
                <option value="single">Faixa única</option>
              </select>
            </label>

            <div className="grid grid-cols-2 gap-2">
              <label className="block rounded-lg border border-surface-200 p-3 dark:border-surface-700">
                <span className="text-xs text-surface-500">Cenas</span>
                <input
                  type="number"
                  min={1}
                  max={10}
                  value={numScenes}
                  onChange={(e) => {
                    setNumScenes(Number(e.target.value));
                    setFormat("custom");
                  }}
                  className="mt-1 w-full bg-transparent text-sm text-surface-900 outline-none dark:text-surface-100"
                />
              </label>
              <label className="block rounded-lg border border-surface-200 p-3 dark:border-surface-700">
                <span className="text-xs text-surface-500">Duração (s)</span>
                <input
                  type="number"
                  min={1}
                  max={MAX_DURATION_SECONDS}
                  value={duration}
                  onChange={(e) => {
                    setDuration(Number(e.target.value));
                    setFormat("custom");
                  }}
                  className="mt-1 w-full bg-transparent text-sm text-surface-900 outline-none dark:text-surface-100"
                />
              </label>
            </div>
          </div>

          {generationError && (
            <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600 dark:bg-red-950/40 dark:text-red-400">
              {generationError}
            </p>
          )}

          <div className="flex items-center justify-between">
            <p className="text-xs text-surface-400">
              Gera um MP4 real (Ollama → frames → FFmpeg) com narração sincronizada por cena.
            </p>
            <Button variant="primary" onClick={handleGenerate} isLoading={generating} disabled={!prompt.trim()}>
              {generating ? "Gerando…" : "▶ Gerar vídeo"}
            </Button>
          </div>
        </CardBody>
      </Card>

      {/* ─── Modules grid ────────────────────────────────────────────── */}
      <div className="mb-8">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
            Módulos do Estúdio
          </h2>
          <Badge variant="primary" size="sm">{readyCount} prontos</Badge>
        </div>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
          {studioModules.map((mod) => (
            <div
              key={mod.name}
              className="group flex flex-col items-center gap-2 rounded-xl border border-surface-200 p-4 text-center transition-all hover:border-primary-300 hover:shadow-md dark:border-surface-700 dark:hover:border-primary-700"
            >
              <div className={`flex h-12 w-12 items-center justify-center rounded-xl ${mod.color} text-xl transition-transform group-hover:scale-110`}>
                {mod.icon}
              </div>
              <p className="text-xs font-semibold text-surface-900 dark:text-surface-50">{mod.name}</p>
              <p className="text-[10px] leading-tight text-surface-400">{mod.desc}</p>
              <span className="mt-auto inline-flex items-center gap-1 rounded-full bg-green-50 px-2 py-0.5 text-[10px] font-medium text-green-600 dark:bg-green-950 dark:text-green-400">
                <span className="h-1 w-1 rounded-full bg-green-500" /> Ativo
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* ─── Planned modules (6 missing) ─────────────────────────────── */}
      <div className="mb-8">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
            Próximos Módulos
          </h2>
          <Badge variant="default" size="sm">{plannedModules.length} em breve</Badge>
        </div>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
          {plannedModules.map((mod) => (
            <div
              key={mod.name}
              className="flex flex-col items-center gap-2 rounded-xl border border-dashed border-surface-300 p-4 text-center opacity-70 dark:border-surface-600"
              title="Módulo em construção"
            >
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-surface-100 text-xl grayscale dark:bg-surface-800">
                {mod.icon}
              </div>
              <p className="text-xs font-semibold text-surface-700 dark:text-surface-300">{mod.name}</p>
              <p className="text-[10px] leading-tight text-surface-400">{mod.desc}</p>
              <span className="mt-auto inline-flex items-center gap-1 rounded-full bg-amber-50 px-2 py-0.5 text-[10px] font-medium text-amber-600 dark:bg-amber-950 dark:text-amber-400">
                ⏳ Em breve
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* ─── Visual edit timeline ──────────────────────────────────── */}
      {(() => {
        const activeJob = jobs.find((job) => job.job_id === activeTimelineJobId);
        if (!activeJob?.edit_timeline) return null;
        return <EditTimelinePanel jobId={activeJob.job_id} editedOutputUrl={activeJob.edited_output_url} sceneAssets={activeJob.scene_assets} timeline={activeJob.edit_timeline} title={`Editor visual · ${activeJob.job_id.slice(0, 8)}`} />;
      })()}

      {/* ─── Jobs ────────────────────────────────────────────────────── */}
      <Card>
        <CardHeader>
          <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">
            Gerações recentes
          </h2>
          <Button variant="ghost" size="sm" onClick={refreshJobs}>⟳ Atualizar</Button>
        </CardHeader>
        <CardBody>
          {jobs.length === 0 ? (
            <p className="py-6 text-center text-sm text-surface-400">
              Nenhuma geração ainda. Use o painel acima para criar o primeiro vídeo.
            </p>
          ) : (
            <div className="space-y-2">
              {jobs.slice(0, 8).map((job) => (
                <div key={job.job_id} className="flex flex-col gap-2 rounded-lg border border-surface-100 p-3 dark:border-surface-800 sm:flex-row sm:items-center sm:justify-between">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <Badge variant={jobStatusVariant(job.status)} size="sm" dot>
                        {job.status}
                      </Badge>
                      <span className="truncate text-xs text-surface-500">{job.job_id.slice(0, 8)}</span>
                      {(() => {
                        const preset = formatPresetFor(job.format);
                        return preset ? (
                          <span className="inline-flex shrink-0 items-center gap-1 rounded-full bg-primary-50 px-2 py-0.5 text-[10px] font-medium text-primary-600 dark:bg-primary-950/60 dark:text-primary-400">
                            <span>{preset.icon}</span>
                            <span>{formatLabel(job.format)}</span>
                          </span>
                        ) : null;
                      })()}
                    </div>
                    {job.status === "processing" && (
                      <div className="mt-2 w-full sm:max-w-md">
                        {/* All frames rendered but audio/voiceover still muxing →
                            show a generic finalizing step instead of a stale
                            "Rendering frames" label. */}
                        {(() => {
                          const framesDone =
                            !!job.total_frames &&
                            (job.frames_rendered ?? 0) >= job.total_frames;
                          const step = framesDone ? "Finalizando (áudio/encode)…" : (job.current_step ?? "Processando…");
                          const counter = job.total_frames
                            ? `${(job.frames_rendered ?? 0).toLocaleString("pt-BR")} / ${job.total_frames.toLocaleString("pt-BR")} frames`
                            : `${Math.round(job.progress * 100)}%`;
                          return (
                            <>
                              <div className="mb-1 flex items-center justify-between gap-2 text-xs text-surface-400">
                                <span className="truncate">{step}</span>
                                <span className="shrink-0 tabular-nums">
                                  {framesDone ? `${Math.round(job.progress * 100)}%` : counter}
                                </span>
                              </div>
                              <div
                                className="h-1.5 w-full overflow-hidden rounded-full bg-surface-100 dark:bg-surface-800"
                                role="progressbar"
                                aria-valuenow={Math.round(job.progress * 100)}
                                aria-valuemin={0}
                                aria-valuemax={100}
                              >
                                <div
                                  className="h-full rounded-full bg-gradient-to-r from-primary-500 to-fuchsia-500 transition-all duration-500"
                                  style={{ width: `${Math.round(Math.min(1, Math.max(0, job.progress)) * 100)}%` }}
                                />
                              </div>
                            </>
                          );
                        })()}
                      </div>
                    )}
                    {(job.video_duration != null || job.voiceover?.muxed) && (
                      <p className="mt-1 text-xs text-surface-400">
                        {job.video_duration != null && (
                          <>⏱️ {fmtDuration(job.video_duration)}</>
                        )}
                        {job.video_duration != null && job.voiceover?.muxed && " · "}
                        {job.voiceover?.muxed && (
                          <>🎙️ {job.voiceover.narration_style === "per_scene" ? `${job.voiceover.clips?.length ?? 0} cenas narradas` : "narração única"}</>
                        )}
                      </p>
                    )}
                    {job.subtitles?.cue_count != null && (
                      <p className="mt-1 text-xs text-surface-400">
                        💬 {job.subtitles.cue_count} legendas SRT geradas
                      </p>
                    )}
                    {job.subtitles?.reason && (
                      <p className="mt-1 text-xs text-amber-500">Legendas: {job.subtitles.reason}</p>
                    )}
                    {job.scene_clips && job.scene_clips.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-2 text-xs">
                        <span className="text-surface-500">Clipes VidGrid:</span>
                        {job.scene_clips.map((clip) => (
                          clip.output_url ? <a key={clip.scene_index} href={clip.output_url} target="_blank" rel="noreferrer" className="font-medium text-primary-600 hover:underline dark:text-primary-400">
                            Cena {clip.scene_index + 1} · {clip.duration}s{clip.audio_status === "per_scene_narration_muxed" ? " · com narração" : clip.audio_status === "single_track_not_split" ? " · sem faixa individual" : ""}
                          </a> : <span key={clip.scene_index} className="text-surface-400">Cena {clip.scene_index + 1} · link indisponível</span>
                        ))}
                      </div>
                    )}
                    {job.error && <p className="mt-1 text-xs text-red-500">{job.error}</p>}
                  </div>
                  <div className="flex shrink-0 items-center gap-3">
                    {job.resolution && job.status === "completed" && (
                      <span className="text-xs text-surface-400">{job.resolution}</span>
                    )}
                    {job.file_size_bytes != null && job.file_size_bytes > 0 && (
                      <span className="text-xs text-surface-400">{fmtBytes(job.file_size_bytes)}</span>
                    )}
                    {job.edit_timeline && job.status === "completed" && (
                      <Button variant="secondary" size="sm" onClick={() => setActiveTimelineJobId((current) => current === job.job_id ? null : job.job_id)}>
                        {activeTimelineJobId === job.job_id ? "Fechar editor" : "Abrir editor"}
                      </Button>
                    )}
                    {job.output_url && job.status === "completed" && (
                      <Button variant="secondary" size="sm" onClick={() => window.open(job.output_url as string, "_blank")}>
                        ⬇ Baixar MP4
                      </Button>
                    )}
                    {job.subtitles?.download_url && job.status === "completed" && (
                      <Button variant="secondary" size="sm" onClick={() => window.open(job.subtitles?.download_url as string, "_blank")}>
                        ⬇ Baixar SRT
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardBody>
      </Card>

      {/* ─── Back link ───────────────────────────────────────────────── */}
      <div className="mt-6">
        <Link href="/dashboard" className="text-sm text-primary-600 hover:text-primary-700 dark:text-primary-400">
          ← Voltar ao Dashboard
        </Link>
      </div>
    </DashboardLayout>
  );
}
