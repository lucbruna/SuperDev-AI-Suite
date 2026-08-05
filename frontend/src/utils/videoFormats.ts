// ---------------------------------------------------------------------------
// Video format presets + pure helpers for the AI Video Studio generation panel.
//
// A "format preset" adjusts duration + resolution + fps together so one click
// produces the right profile for a target platform (vertical 9:16 Shorts /
// Reels / TikTok, landscape YouTube, square 1:1). Also holds the duration
// presets and the render-time estimate logic shown in the panel warning.
// Generic formatters (bytes/durations/badge variants) live in ``format.ts``.
// Keeping this module free of React makes it trivially unit-testable.
// ---------------------------------------------------------------------------

export interface ResolutionPreset {
  label: string;
  value: string; // "WxH" sent to the backend
  pixels: number;
}

export interface VideoFormatPreset {
  value: string;
  label: string;
  icon: string;
  aspect: string; // "9:16"
  resolution: string; // "WxH"
  fps: number;
  duration: number; // default duration in seconds
  hint: string;
}

// Landscape resolution presets (independent of the platform formats below).
export const RESOLUTION_PRESETS: ResolutionPreset[] = [
  { label: "720p", value: "1280x720", pixels: 1280 * 720 },
  { label: "1080p", value: "1920x1080", pixels: 1920 * 1080 },
  { label: "4K", value: "3840x2160", pixels: 3840 * 2160 },
];

export const FPS_PRESETS = [24, 30, 60];

// Platform presets — each sets duration + resolution + fps in one click.
// Durations are sensible defaults for the platform; the user can still pick a
// different duration preset afterwards (which switches back to "custom").
export const FORMAT_PRESETS: VideoFormatPreset[] = [
  {
    value: "shorts",
    label: "YouTube Shorts",
    icon: "📱",
    aspect: "9:16",
    resolution: "1080x1920",
    fps: 30,
    duration: 30,
    hint: "9:16 · 1080×1920 · 30fps",
  },
  {
    value: "reels",
    label: "Reels",
    icon: "📸",
    aspect: "9:16",
    resolution: "1080x1920",
    fps: 30,
    duration: 30,
    hint: "9:16 · 1080×1920 · 30fps",
  },
  {
    value: "tiktok",
    label: "TikTok",
    icon: "🎵",
    aspect: "9:16",
    resolution: "1080x1920",
    fps: 30,
    duration: 15,
    hint: "9:16 · 1080×1920 · 30fps",
  },
  {
    value: "youtube",
    label: "YouTube 16:9",
    icon: "▶️",
    aspect: "16:9",
    resolution: "1920x1080",
    fps: 24,
    duration: 60,
    hint: "16:9 · 1080p · 24fps",
  },
  {
    value: "square",
    label: "Quadrado 1:1",
    icon: "⬜",
    aspect: "1:1",
    resolution: "1080x1080",
    fps: 24,
    duration: 15,
    hint: "1:1 · 1080×1080 · 24fps",
  },
];

/** Fallback used when a resolution string cannot be parsed (≈720p). */
const FALLBACK_PIXELS = 1280 * 720;

/** Parse a "WxH" resolution string into a pixel count (safe fallback). */
export function parseResolutionPixels(value: string): number {
  // Mirror the backend (_parse_resolution): tolerate uppercase X and ":".
  const parts = value
    .toLowerCase()
    .replace(":", "x")
    .split("x")
    .map((s) => parseInt(s.trim(), 10));
  const width = parts[0];
  const height = parts[1];
  if (!width || !height || Number.isNaN(width) || Number.isNaN(height)) {
    return FALLBACK_PIXELS;
  }
  return width * height;
}

/** Short display label for a "WxH" value (falls back to the raw string). */
export function resolutionLabel(value: string): string {
  const preset = RESOLUTION_PRESETS.find((r) => r.value === value);
  return preset ? preset.label : value;
}

/**
 * Find the preset matching a persisted job format value.
 * Returns null for "custom" (user tweaked a dimension), missing or unknown
 * values — the list falls back to the raw resolution display in that case.
 */
export function formatPresetFor(
  value: string | null | undefined,
): VideoFormatPreset | null {
  if (!value || value === "custom") return null;
  return FORMAT_PRESETS.find((p) => p.value === value) ?? null;
}

/**
 * Human-readable label for a persisted job format value, e.g. "YouTube
 * Shorts 9:16". Labels that already carry the aspect ratio ("YouTube 16:9",
 * "Quadrado 1:1") are not duplicated.
 */
export function formatLabel(value: string | null | undefined): string | null {
  const preset = formatPresetFor(value);
  if (!preset) return null;
  return /[0-9]:[0-9]/.test(preset.label)
    ? preset.label
    : `${preset.label} ${preset.aspect}`;
}

/**
 * Recommended duration (seconds) for an active platform format preset, or
 * null when the format is custom/unknown. Mirrors the preset's default
 * duration so the panel can highlight the matching DURATION_PRESETS chip.
 */
export function recommendedDurationFor(
  value: string | null | undefined,
): number | null {
  const preset = formatPresetFor(value);
  return preset ? preset.duration : null;
}

export interface DurationPreset {
  label: string;
  seconds: number;
}

// Duration the user can pick with one click (up to the 10 min cap).
// The last entry must stay in sync with MAX_DURATION_SECONDS.
export const DURATION_PRESETS: DurationPreset[] = [
  { label: "10s", seconds: 10 },
  { label: "15s", seconds: 15 },
  { label: "30s", seconds: 30 },
  { label: "1 min", seconds: 60 },
  { label: "2 min", seconds: 120 },
  { label: "3 min", seconds: 180 },
  { label: "5 min", seconds: 300 },
  { label: "10 min", seconds: 600 },
];

// Hard cap on video length (mirrors the backend `le=600` on duration_seconds).
export const MAX_DURATION_SECONDS = 600;

/**
 * Rough render-time estimate for long videos (single-core CPU).
 *
 * Calibrated against a real ``render_multi_scene_video`` benchmark at 720p:
 * PIL frame rendering + FFmpeg encode measured ~0.30s per 1M frame-pixels.
 * We use 0.35s to leave a small safety margin for slower machines.
 */
export function estimateRenderSeconds(
  durationSeconds: number,
  fps: number,
  pixels: number,
): number {
  const totalFrames = durationSeconds * fps;
  const perFramePixel = 0.35 / 1_000_000;
  const seconds = totalFrames * pixels * perFramePixel;
  return Math.max(seconds, durationSeconds * 0.5);
}


