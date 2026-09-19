"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { DashboardLayout } from "@/components/DashboardLayout";
import { Card, CardHeader, CardBody } from "@/components/cards/Card";
import { Badge } from "@/components/badges/Badge";
import { Button } from "@/components/buttons/Button";
import {
  multimediaApi,
  type MultimediaHealth,
  type RunOperationResult,
  type SubsystemCapability,
} from "@/api/multimedia";
import { extractErrorMessage } from "@/utils/apiError";
import { studioHealthVariant } from "@/utils/format";

// ---------------------------------------------------------------------------
// Real subsystems already implemented in modules/multimedia_ai_engine/
// ---------------------------------------------------------------------------

const subsystemMeta: Record<string, { icon: string; desc: string; color: string }> = {
  ai_avatar_engine: {
    icon: "🧑‍🚀",
    desc: "Avatares, facial, lipsync e render",
    color: "bg-violet-50 text-violet-600 dark:bg-violet-950 dark:text-violet-400",
  },
  ai_render_farm: {
    icon: "🖥️",
    desc: "Render distribuído, GPU e cache",
    color: "bg-blue-50 text-blue-600 dark:bg-blue-950 dark:text-blue-400",
  },
  ai_video_analytics: {
    icon: "📊",
    desc: "Detecção, tracking e métricas",
    color: "bg-emerald-50 text-emerald-600 dark:bg-emerald-950 dark:text-emerald-400",
  },
  ai_speech_analytics: {
    icon: "🎙️",
    desc: "Transcrição, diarização e sentimentos",
    color: "bg-amber-50 text-amber-600 dark:bg-amber-950 dark:text-amber-400",
  },
  ai_streaming_engine: {
    icon: "📡",
    desc: "Live, transcodificação e delivery",
    color: "bg-rose-50 text-rose-600 dark:bg-rose-950 dark:text-rose-400",
  },
};

const sampleParams: Record<string, Record<string, unknown>> = {
  generate_avatar: { style: "anime", resolution: "1080p" },
  animate: { avatar_id: "avatar_1", animation: "walk", frames: 30 },
  submit_render: { scene: "scene_a", start_frame: 0, end_frame: 20, format: "png" },
  process_next: {},
  analyze_video: { video_id: "clip_1", frame_count: 30, detectors: ["object", "face"] },
  analyze_speech: { audio_id: "call_1", transcript: "This is a great product. I love it." },
  start_stream: { channel_id: "channel-1", stream_key: "live_stream_key_001", protocol: "hls" },
  get_playback_url: { channel_id: "channel-1" },
};

function prettyJson(value: unknown): string {
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
}

function subsystemLabel(name: string): string {
  return name.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export default function MultimediaPage() {
  const [health, setHealth] = useState<MultimediaHealth | null>(null);
  const [healthState, setHealthState] = useState<string>("checking");
  const [subsystems, setSubsystems] = useState<SubsystemCapability[]>([]);

  // Operation console state
  const [selectedSubsystem, setSelectedSubsystem] = useState<string>("ai_avatar_engine");
  const [selectedOperation, setSelectedOperation] = useState<string>("generate_avatar");
  const [paramsText, setParamsText] = useState<string>(prettyJson(sampleParams.generate_avatar));
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<RunOperationResult | null>(null);
  const [resultError, setResultError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const h = await multimediaApi.health();
        if (!cancelled) {
          setHealth(h);
          setHealthState(h.status);
        }
      } catch {
        if (!cancelled) setHealthState("offline");
      }
      try {
        const caps = await multimediaApi.capabilities();
        if (!cancelled) setSubsystems(caps.subsystems);
      } catch {
        // backend may be offline
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const refreshHealth = useCallback(async () => {
    try {
      const h = await multimediaApi.health();
      setHealth(h);
      setHealthState(h.status);
    } catch {
      setHealthState("offline");
    }
  }, []);

  const activeSubsystem = subsystems.find((s) => s.name === selectedSubsystem);

  const selectSubsystem = (name: string) => {
    setSelectedSubsystem(name);
    const ops = subsystems.find((s) => s.name === name)?.operations ?? [];
    const firstOp = ops[0] ?? "";
    setSelectedOperation(firstOp);
    const sample = sampleParams[firstOp];
    setParamsText(sample ? prettyJson(sample) : "{}");
    setResult(null);
    setResultError(null);
  };

  const selectOperation = (op: string) => {
    setSelectedOperation(op);
    const sample = sampleParams[op];
    setParamsText(sample ? prettyJson(sample) : "{}");
    setResult(null);
    setResultError(null);
  };

  const handleRun = async () => {
    setRunning(true);
    setResultError(null);
    try {
      let params: Record<string, unknown> = {};
      try {
        params = paramsText.trim() ? JSON.parse(paramsText) : {};
      } catch {
        throw new Error("Parâmetros inválidos — precisa ser JSON válido");
      }
      const data = await multimediaApi.run(selectedSubsystem, selectedOperation, params);
      setResult(data);
    } catch (e) {
      setResultError(extractErrorMessage(e, "Falha ao executar operação"));
      setResult(null);
    } finally {
      setRunning(false);
    }
  };

  const totalOps = subsystems.reduce((acc, s) => acc + (s.operations?.length ?? 0), 0);

  return (
    <DashboardLayout>
      {/* ─── Header ──────────────────────────────────────────────────── */}
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-fuchsia-500 to-indigo-600 text-2xl shadow-lg">
            🎛️
          </div>
          <div>
            <h1 className="text-2xl font-bold text-surface-900 dark:text-surface-50">
              Multimedia AI Engine
            </h1>
            <p className="mt-0.5 text-sm text-surface-500">
              Motor autônomo de mídia — {subsystems.length} subsistemas · {totalOps} operações
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant={studioHealthVariant(healthState)} size="md" dot={healthState !== "checking"}>
            {healthState === "checking" && "Verificando…"}
            {healthState === "active" && "Backend conectado"}
            {healthState === "degraded" && "Degradado"}
            {healthState === "offline" && "Backend offline"}
          </Badge>
          <Button variant="secondary" size="sm" onClick={refreshHealth}>
            ⟳ Atualizar
          </Button>
        </div>
      </div>

      {/* ─── Subsystem grid ──────────────────────────────────────────── */}
      <div className="mb-8">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">Subsistemas</h2>
          <Badge variant="primary" size="sm">{subsystems.length} registrados</Badge>
        </div>
        {subsystems.length === 0 ? (
          <p className="rounded-lg border border-surface-200 bg-surface-50 p-4 text-sm text-surface-500 dark:border-surface-700 dark:bg-surface-800/50">
            Nenhum subsistema carregado. Verifique se o backend está rodando.
          </p>
        ) : (
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
            {subsystems.map((sub) => {
              const meta = subsystemMeta[sub.name] ?? {
                icon: "🧩",
                desc: sub.name,
                color: "bg-surface-100 text-surface-600 dark:bg-surface-800 dark:text-surface-300",
              };
              const active = selectedSubsystem === sub.name;
              const isHealthy = health?.subsystems?.[sub.name]?.status === "active";
              return (
                <button
                  key={sub.name}
                  type="button"
                  onClick={() => selectSubsystem(sub.name)}
                  className={`flex flex-col items-center gap-2 rounded-xl border p-4 text-center transition-all hover:shadow-md ${
                    active
                      ? "border-primary-400 bg-primary-50 shadow-md dark:border-primary-600 dark:bg-primary-950/40"
                      : "border-surface-200 hover:border-primary-300 dark:border-surface-700 dark:hover:border-primary-700"
                  }`}
                >
                  <div className={`flex h-12 w-12 items-center justify-center rounded-xl ${meta.color} text-xl transition-transform group-hover:scale-110`}>
                    {meta.icon}
                  </div>
                  <p className="text-xs font-semibold text-surface-900 dark:text-surface-50">{subsystemLabel(sub.name)}</p>
                  <p className="text-[10px] leading-tight text-surface-400">{meta.desc}</p>
                  <div className="mt-auto flex items-center gap-1.5">
                    <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-medium ${
                      isHealthy
                        ? "bg-green-50 text-green-600 dark:bg-green-950 dark:text-green-400"
                        : "bg-amber-50 text-amber-600 dark:bg-amber-950 dark:text-amber-400"
                    }`}>
                      <span className={`h-1 w-1 rounded-full ${isHealthy ? "bg-green-500" : "bg-amber-500"}`} />
                      {sub.status}
                    </span>
                    <span className="text-[10px] text-surface-400">v{sub.version}</span>
                  </div>
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* ─── Operation console ───────────────────────────────────────── */}
      <Card className="mb-8">
        <CardHeader>
          <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">Console de operações</h2>
          <Badge variant="info" size="sm">Dispatch via registry</Badge>
        </CardHeader>
        <CardBody>
          <div className="grid gap-4 lg:grid-cols-2">
            <div>
              <p className="mb-2 text-xs font-medium text-surface-500">⚙️ Operação</p>
              <div className="flex flex-wrap gap-2">
                {(activeSubsystem?.operations ?? []).map((op) => {
                  const active = selectedOperation === op;
                  return (
                    <button
                      key={op}
                      type="button"
                      aria-pressed={active}
                      onClick={() => selectOperation(op)}
                      className={`rounded-lg px-3 py-1.5 font-mono text-xs font-medium transition-all ${
                        active
                          ? "bg-primary-600 text-white shadow-sm"
                          : "bg-surface-100 text-surface-700 hover:bg-surface-200 dark:bg-surface-800 dark:text-surface-300 dark:hover:bg-surface-700"
                      }`}
                    >
                      {op}
                    </button>
                  );
                })}
              </div>

              <p className="mb-2 mt-5 text-xs font-medium text-surface-500">📦 Parâmetros (JSON)</p>
              <textarea
                value={paramsText}
                onChange={(e) => setParamsText(e.target.value)}
                rows={8}
                spellCheck={false}
                className="w-full rounded-lg border border-surface-300 bg-surface-50 px-3 py-2 font-mono text-xs text-surface-900 outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 dark:border-surface-600 dark:bg-surface-900 dark:text-surface-100"
              />
              <div className="mt-3 flex items-center justify-between">
                <p className="text-xs text-surface-400">
                  <span className="font-mono">{selectedSubsystem}</span> / <span className="font-mono">{selectedOperation}</span>
                </p>
                <Button variant="primary" onClick={handleRun} isLoading={running} disabled={!selectedOperation}>
                  {running ? "Executando…" : "▶ Executar"}
                </Button>
              </div>
            </div>

            <div>
              <p className="mb-2 text-xs font-medium text-surface-500">📄 Resultado</p>
              {resultError ? (
                <div className="rounded-lg border border-red-200 bg-red-50 p-3 font-mono text-xs text-red-600 dark:border-red-900/60 dark:bg-red-950/40 dark:text-red-400">
                  {resultError}
                </div>
              ) : result ? (
                <pre className="max-h-80 overflow-auto rounded-lg border border-surface-200 bg-surface-50 p-3 font-mono text-xs text-surface-800 dark:border-surface-700 dark:bg-surface-900 dark:text-surface-200">
                  {prettyJson(result)}
                </pre>
              ) : (
                <div className="flex h-full min-h-40 items-center justify-center rounded-lg border border-dashed border-surface-300 text-sm text-surface-400 dark:border-surface-600">
                  Execute uma operação para ver o resultado aqui.
                </div>
              )}
            </div>
          </div>
        </CardBody>
      </Card>

      {/* ─── Health panel ────────────────────────────────────────────── */}
      <Card>
        <CardHeader>
          <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">Status dos subsistemas</h2>
          <Badge variant={studioHealthVariant(healthState)} size="sm">
            {healthState}
          </Badge>
        </CardHeader>
        <CardBody>
          {health && health.subsystems ? (
            <div className="space-y-2">
              {Object.entries(health.subsystems).map(([name, info]) => (
                <div
                  key={name}
                  className="flex flex-col gap-1 rounded-lg border border-surface-100 p-3 dark:border-surface-800 sm:flex-row sm:items-center sm:justify-between"
                >
                  <div className="flex items-center gap-2">
                    <Badge variant={studioHealthVariant(info.status)} size="sm" dot>
                      {info.status}
                    </Badge>
                    <span className="text-sm font-medium text-surface-900 dark:text-surface-100">
                      {subsystemLabel(name)}
                    </span>
                  </div>
                  {info.details && Object.keys(info.details).length > 0 && (
                    <span className="text-xs text-surface-400">
                      {prettyJson(info.details).slice(0, 120)}
                    </span>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="py-6 text-center text-sm text-surface-400">
              {healthState === "offline" ? "Backend offline — não foi possível carregar o status." : "Carregando status…"}
            </p>
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
