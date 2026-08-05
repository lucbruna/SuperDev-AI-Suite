"""Effects engine — registry-driven visual effects applied to real frames.

Every effect is a pure ``apply(frame, params) -> frame`` function registered by
name. The engine validates parameters, provides shared blend/blur helpers and
applies effects in sequence (a clip's effect list runs in order).
"""
from __future__ import annotations

from typing import Any, Callable

import numpy as np

from modules.ai_video_studio.editor_common import Registry, as_rgb, clamp, make_logger

logger = make_logger("effects.engine")


# ── Shared helpers used by many effects ──────────────────────────
def gaussian_blur(arr: np.ndarray, radius: float) -> np.ndarray:
    """Blur a float [0,1] HxWxC array with a Gaussian via Pillow."""
    if radius <= 0:
        return arr
    from PIL import Image, ImageFilter

    img = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
    return np.asarray(img.filter(ImageFilter.GaussianBlur(radius)), dtype=np.float32) / 255.0


def box_blur(arr: np.ndarray, radius: int) -> np.ndarray:
    """Fast separable box blur on a float [0,1] HxWxC array."""
    radius = max(1, int(radius))
    out = arr.copy()
    k = 2 * radius + 1
    for _ in range(2):
        kernel = np.ones(k, dtype=np.float32) / k
        for c in range(out.shape[-1]):
            out[..., c] = np.apply_along_axis(lambda m: np.convolve(m, kernel, mode="same"), 0, out[..., c])
        out = np.transpose(out, (1, 0, 2))
    return out


def screen_blend(base: np.ndarray, overlay: np.ndarray) -> np.ndarray:
    return 1.0 - (1.0 - base) * (1.0 - overlay)


def linear_dodge(base: np.ndarray, overlay: np.ndarray) -> np.ndarray:
    return np.clip(base + overlay, 0.0, 1.0)


def add_glow(arr: np.ndarray, intensity: float = 0.5) -> np.ndarray:
    """Add a soft halo glow derived from the bright regions of ``arr``.

    Works on a float [0,1] HxWxC array: the luma-boosted signal is blurred
    and additively blended back, weighted by ``intensity``.
    """
    img = np.asarray(arr, dtype=np.float32)
    luma = img @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    bright = np.clip(luma - 0.35, 0.0, 1.0) ** 2
    glow = gaussian_blur(bright[..., None], radius=max(1.0, min(img.shape[:2]) * 0.02))
    return np.clip(img + glow * np.float32(intensity), 0.0, 1.0)


def make_fire_particles(
    n: int,
    frame_shape: tuple[int, int],
    center: tuple[int, int],
    rng: np.random.Generator,
    spread: float,
) -> np.ndarray:
    """Generate ``n`` fire-particle positions clustered near ``center``.

    Returns a (N, 2) float array of (x, y) coordinates in frame space,
    biased upward (fire rises) with an exponential falloff by distance.
    """
    cx, cy = center
    r = rng.exponential(scale=max(1.0, spread), size=n)
    theta = rng.uniform(-np.pi, np.pi, size=n)
    x = cx + r * np.cos(theta)
    y = cy - r * np.abs(np.sin(theta)) * 0.9  # bias upward
    return np.stack([x, y], axis=-1)


def make_spark_particles(
    n: int,
    frame_shape: tuple[int, int],
    center: tuple[int, int],
    rng: np.random.Generator,
    spread: float,
) -> np.ndarray:
    """Generate ``n`` spark positions radiating outward from ``center``.

    Sparks are elongated away from the source: radial direction with a
    narrower angular scatter and a heavier tail than fire particles.
    """
    cx, cy = center
    r = rng.exponential(scale=max(1.0, spread), size=n)
    theta = rng.uniform(-np.pi, np.pi, size=n)
    x = cx + r * np.cos(theta)
    y = cy + r * np.sin(theta) * 0.55
    return np.stack([x, y], axis=-1)


def draw_particles(
    base: np.ndarray,
    particles: np.ndarray,
    color: tuple[float, float, float],
    *,
    radius: float = 2.0,
    alpha: float = 0.8,
    additive: bool = True,
) -> np.ndarray:
    """Draw a (N, 2) particle position array onto a float [0,1] frame.

    Particles are rasterized as discs via a small neighbourhood grid around
    each position. When ``additive`` the discs brighten (light/glow);
    otherwise they alpha-blend (smoke/soft dust).
    """
    img = np.asarray(base, dtype=np.float32).copy()
    h, w = img.shape[:2]
    color_arr = np.array(color, dtype=np.float32)
    r = int(max(1.0, radius))
    for px, py in particles:
        cx, cy = int(round(px)), int(round(py))
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                x, y = cx + dx, cy + dy
                if 0 <= x < w and 0 <= y < h:
                    dist = (dx * dx + dy * dy) / max(1, r * r)
                    falloff = max(0.0, 1.0 - dist)
                    if additive:
                        img[y, x] += color_arr * (alpha * falloff)
                    else:
                        img[y, x] = img[y, x] * (1 - alpha * falloff) + color_arr * (alpha * falloff)
    return np.clip(img, 0.0, 1.0)


class EffectsEngine:
    def __init__(self) -> None:
        self.registry = Registry("effect")

    def register(self, name: str, fn: Callable[..., Any], **meta: Any) -> None:
        self.registry.register(name, fn, **meta)

    def apply(self, name: str, frame: Any, params: dict[str, Any] | None = None) -> np.ndarray:
        """Apply one effect by name to a frame; returns uint8 RGB."""
        fn = self.registry.get(name)
        result = fn(as_rgb(frame), params or {})
        return as_rgb(result)

    def apply_chain(self, frame: Any, effects: list[dict[str, Any]]) -> np.ndarray:
        """Apply a clip's effect list (in order) to a frame."""
        result = as_rgb(frame)
        for effect in effects:
            result = self.apply(effect.get("name", ""), result, effect.get("params", {}))
        return result

    def names(self) -> list[str]:
        return self.registry.names()

    def describe(self, name: str) -> dict[str, Any]:
        return self.registry.meta(name)


_engine: EffectsEngine | None = None


def get_effects_engine() -> EffectsEngine:
    """Cached engine with all built-in effects registered."""
    global _engine
    if _engine is None:
        _engine = EffectsEngine()
        from modules.ai_video_studio.ai_effects.effects_library import register_builtin_effects

        register_builtin_effects(_engine)
    return _engine
