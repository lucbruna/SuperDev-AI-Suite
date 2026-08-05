"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { DashboardLayout } from "@/components/DashboardLayout";
import { Card, CardHeader, CardBody } from "@/components/cards/Card";
import { Badge } from "@/components/badges/Badge";
import { Button } from "@/components/buttons/Button";
import { useAuthStore } from "@/stores/authStore";
import { videoStudioApi, type StudioJob, type StudioVoice } from "@/api/videoStudio";
import { extractErrorMessage } from "@/utils/apiError";
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

  // Generation form state
  const [prompt, setPrompt] = useState("A cinematic drone shot over a misty mountain range at sunrise, with a voiceover narration");
  const [voiceover, setVoiceover] = useState(true);
  const [voiceId, setVoiceId] = useState("default");
  const [mode, setMode] = useState<"per_scene" | "single">("per_scene");
  const [numScenes, setNumScenes] = useState(3);
  const [duration, setDuration] = useState(6);
  const [resolution, setResolution] = useState<string>(RESOLUTION_PRESETS[0].value);
  const [frameRate, setFrameRate] = useState<number>(FPS_PRESETS[0]);
  // Active platform format preset ("custom" once the user tweaks any dimension).
  const [format, setFormat] = useState<string>("custom");
  const [generating, setGenerating] = useState(false);
  const [generationError, setGenerationError] = useState<string | null>(null);
  const pollTimer = useRef<ReturnType<typeof setInterval> | null>(null);

  // Estimated render time for the current resolution/fps/duration combo.
  const estimatedSeconds = estimateRenderSeconds(duration, frameRate, parseResolutionPixels(resolution));
  const isLongVideo = estimatedSeconds >= 180 || duration >= 300;
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
        voiceover,
        voice_id: voiceId,
        voiceover_mode: mode,
        num_scenes: Math.min(20, Math.max(1, numScenes)),
        duration_seconds: Math.min(MAX_DURATION_SECONDS, Math.max(1, duration)),
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

          {/* ── Duration presets ─────────────────────────────────── */}
          <div>
            <p className="mb-2 text-xs font-medium text-surface-500">
              ⏱️ Duração do vídeo
            </p>
            <div className="flex flex-wrap gap-2">
              {DURATION_PRESETS.map((preset) => {
                const active = duration === preset.seconds;
                const suggested = recommendedDuration === preset.seconds;
                return (
                  <button
                    key={preset.seconds}
                    type="button"
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
              Atual: <span className="font-semibold text-surface-600 dark:text-surface-300">{fmtDuration(duration)}</span> · limite de 10 minutos
            </p>
            {activeFormat && recommendedDuration != null && (
              <p className="mt-1 text-xs font-medium text-primary-600 dark:text-primary-400">
                ✨ {activeFormat.label} sugere {fmtDuration(recommendedDuration)} — preset de duração destacado acima
              </p>
            )}
          </div>

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
              {duration}s × {frameRate}fps × {resolutionLabel(resolution)} = {Math.round(duration * frameRate).toLocaleString("pt-BR")} frames
            </span>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <label className="flex items-center gap-2 rounded-lg border border-surface-200 p-3 dark:border-surface-700">
              <input type="checkbox" checked={voiceover} onChange={(e) => setVoiceover(e.target.checked)} className="h-4 w-4 accent-primary-600" />
              <span className="text-sm text-surface-700 dark:text-surface-300">🎙️ Narração</span>
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
                    {job.error && <p className="mt-1 text-xs text-red-500">{job.error}</p>}
                  </div>
                  <div className="flex shrink-0 items-center gap-3">
                    {job.resolution && job.status === "completed" && (
                      <span className="text-xs text-surface-400">{job.resolution}</span>
                    )}
                    {job.file_size_bytes != null && job.file_size_bytes > 0 && (
                      <span className="text-xs text-surface-400">{fmtBytes(job.file_size_bytes)}</span>
                    )}
                    {job.output_url && job.status === "completed" && (
                      <Button variant="secondary" size="sm" onClick={() => window.open(job.output_url as string, "_blank")}>
                        ⬇ Baixar MP4
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
