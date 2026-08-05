import { describe, expect, it } from "vitest";
import {
  DURATION_PRESETS,
  FORMAT_PRESETS,
  MAX_DURATION_SECONDS,
  RESOLUTION_PRESETS,
  estimateRenderSeconds,
  formatLabel,
  formatPresetFor,
  parseResolutionPixels,
  recommendedDurationFor,
  resolutionLabel,
} from "@/utils/videoFormats";

describe("video format presets", () => {
  it("includes the vertical 9:16 social formats", () => {
    const values = FORMAT_PRESETS.map((p) => p.value);
    expect(values).toEqual(
      expect.arrayContaining(["shorts", "reels", "tiktok"]),
    );
  });

  it("Shorts/Reels/TikTok use 9:16 at 1080x1920 and 30fps", () => {
    for (const value of ["shorts", "reels", "tiktok"]) {
      const preset = FORMAT_PRESETS.find((p) => p.value === value)!;
      expect(preset.aspect).toBe("9:16");
      expect(preset.resolution).toBe("1080x1920");
      expect(preset.fps).toBe(30);
    }
  });

  it("every preset carries a valid WxH resolution and positive duration/fps", () => {
    for (const preset of FORMAT_PRESETS) {
      const [w, h] = preset.resolution.split("x").map(Number);
      expect(w).toBeGreaterThan(0);
      expect(h).toBeGreaterThan(0);
      expect(preset.duration).toBeGreaterThan(0);
      expect(preset.fps).toBeGreaterThan(0);
    }
  });

  it("every preset resolution is accepted by the backend parser contract", () => {
    // Backend _parse_resolution requires both dims >= 64.
    for (const preset of FORMAT_PRESETS) {
      const [w, h] = preset.resolution.split("x").map(Number);
      expect(Math.min(w, h)).toBeGreaterThanOrEqual(64);
    }
  });
});

describe("parseResolutionPixels", () => {
  it("computes pixels for vertical 9:16", () => {
    expect(parseResolutionPixels("1080x1920")).toBe(1080 * 1920);
  });

  it("tolerates uppercase X and colon separators like the backend", () => {
    expect(parseResolutionPixels("1080X1920")).toBe(1080 * 1920);
    expect(parseResolutionPixels("1080:1920")).toBe(1080 * 1920);
  });

  it("computes pixels for landscape presets", () => {
    for (const preset of RESOLUTION_PRESETS) {
      expect(parseResolutionPixels(preset.value)).toBe(preset.pixels);
    }
  });

  it("falls back to 720p for garbage input", () => {
    expect(parseResolutionPixels("")).toBe(1280 * 720);
    expect(parseResolutionPixels("abc")).toBe(1280 * 720);
    expect(parseResolutionPixels("1080x")).toBe(1280 * 720);
    expect(parseResolutionPixels("0x0")).toBe(1280 * 720);
  });
});

describe("resolutionLabel", () => {
  it("maps known landscape values to friendly labels", () => {
    expect(resolutionLabel("1920x1080")).toBe("1080p");
    expect(resolutionLabel("1280x720")).toBe("720p");
    expect(resolutionLabel("3840x2160")).toBe("4K");
  });

  it("falls back to the raw WxH string for vertical formats", () => {
    expect(resolutionLabel("1080x1920")).toBe("1080x1920");
  });
});

describe("formatPresetFor", () => {
  it("finds the preset for every known format value", () => {
    for (const preset of FORMAT_PRESETS) {
      expect(formatPresetFor(preset.value)?.value).toBe(preset.value);
    }
  });

  it("returns null for custom, missing and unknown values", () => {
    expect(formatPresetFor("custom")).toBeNull();
    expect(formatPresetFor(null)).toBeNull();
    expect(formatPresetFor(undefined)).toBeNull();
    expect(formatPresetFor("bogus")).toBeNull();
  });
});

describe("formatLabel", () => {
  it("labels vertical social formats with the aspect ratio", () => {
    expect(formatLabel("shorts")).toBe("YouTube Shorts 9:16");
    expect(formatLabel("reels")).toBe("Reels 9:16");
    expect(formatLabel("tiktok")).toBe("TikTok 9:16");
  });

  it("does not duplicate the aspect already in the label", () => {
    expect(formatLabel("youtube")).toBe("YouTube 16:9");
    expect(formatLabel("square")).toBe("Quadrado 1:1");
  });

  it("returns null for custom/missing formats", () => {
    expect(formatLabel("custom")).toBeNull();
    expect(formatLabel(null)).toBeNull();
    expect(formatLabel(undefined)).toBeNull();
  });
});

describe("DURATION_PRESETS", () => {
  it("covers 10s up to the 10-minute cap", () => {
    const seconds = DURATION_PRESETS.map((p) => p.seconds);
    expect(seconds).toEqual([10, 15, 30, 60, 120, 180, 300, 600]);
  });

  it("the longest preset matches MAX_DURATION_SECONDS and the backend cap", () => {
    const last = DURATION_PRESETS[DURATION_PRESETS.length - 1];
    expect(last.seconds).toBe(MAX_DURATION_SECONDS);
    expect(MAX_DURATION_SECONDS).toBe(600); // backend `le=600` on duration_seconds
  });

  it("every preset carries a positive duration and a label", () => {
    for (const preset of DURATION_PRESETS) {
      expect(preset.seconds).toBeGreaterThan(0);
      expect(preset.label.length).toBeGreaterThan(0);
    }
  });

  it("every format's recommended duration is available as a preset chip", () => {
    // The panel highlights the recommended DURATION_PRESETS chip, so the
    // recommendation must always be one-click selectable.
    const presetSeconds = new Set(DURATION_PRESETS.map((p) => p.seconds));
    for (const preset of FORMAT_PRESETS) {
      expect(presetSeconds.has(preset.duration)).toBe(true);
    }
  });
});

describe("recommendedDurationFor", () => {
  it("returns each platform's recommended duration", () => {
    expect(recommendedDurationFor("tiktok")).toBe(15);
    expect(recommendedDurationFor("square")).toBe(15);
    expect(recommendedDurationFor("shorts")).toBe(30);
    expect(recommendedDurationFor("reels")).toBe(30);
    expect(recommendedDurationFor("youtube")).toBe(60);
  });

  it("returns null for custom, missing and unknown formats", () => {
    expect(recommendedDurationFor("custom")).toBeNull();
    expect(recommendedDurationFor(null)).toBeNull();
    expect(recommendedDurationFor(undefined)).toBeNull();
    expect(recommendedDurationFor("bogus")).toBeNull();
  });
});

describe("estimateRenderSeconds", () => {
  it("scales with frames x pixels (calibrated ~0.35s per 1M frame-pixels)", () => {
    // 6s @ 24fps @ 720p = 144 frames * 921,600 px.
    const est = estimateRenderSeconds(6, 24, 1280 * 720);
    expect(est).toBeCloseTo(144 * (1280 * 720) * (0.35 / 1_000_000), 1);
    expect(est).toBeCloseTo(46.4, 1);
  });

  it("doubling fps or pixels doubles the estimate", () => {
    const base = estimateRenderSeconds(10, 24, 1280 * 720);
    expect(estimateRenderSeconds(10, 48, 1280 * 720)).toBeCloseTo(base * 2, 6);
    expect(estimateRenderSeconds(10, 24, 2560 * 1440)).toBeCloseTo(base * 4, 6);
  });

  it("never falls below half the video length (floor for tiny renders)", () => {
    // Tiny render would compute ~0.08s — the floor (duration * 0.5) must win.
    expect(estimateRenderSeconds(1, 1, 640 * 360)).toBe(0.5);
  });

  it("flags a 10-minute 4K video as a long render", () => {
    const est = estimateRenderSeconds(600, 30, 3840 * 2160);
    expect(est).toBeGreaterThan(180); // > 3 min warning threshold
  });
});
