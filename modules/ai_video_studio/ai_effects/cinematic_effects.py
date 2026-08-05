"""Cinematic effect presets — high-level combinations of the basic effects.

Every preset follows the studio-wide ``apply(frame, params) -> frame`` contract
(returns uint8 RGB) so it can be registered in the effects registry and chained
with any other effect. Each preset composes several low-level effect operations
into a single "cinematic look", mirroring what a pro NLE bundles as a preset.
"""
from __future__ import annotations

from typing import Any

import numpy as np

from modules.ai_video_studio.ai_effects.chromatic_aberration import apply as _ca
from modules.ai_video_studio.ai_effects.effects_engine import gaussian_blur
from modules.ai_video_studio.ai_effects.film_grain import apply as _grain
from modules.ai_video_studio.ai_effects.lens_flare import apply as _flare
from modules.ai_video_studio.ai_effects.vignette import apply as _vignette
from modules.ai_video_studio.editor_common import as_rgb, clamp


def anamorphic_look(frame: Any, params: dict[str, Any] | None = None) -> np.ndarray:
    """Anamorphic lens emulation: horizontal flare + chromatic aberration."""
    p = params or {}
    out = _flare(
        frame,
        {
            "x": 0.5,
            "y": 0.5,
            "strength": float(p.get("flare_strength", 0.35)),
            "color": list(p.get("flare_color", [60 / 255, 120 / 255, 1.0])),
        },
    )
    out = _ca(out, {"amount": float(p.get("ca_strength", 0.6))})
    out = _grain(out, {"strength": float(p.get("grain", 0.02)), "seed": 7})
    out = _vignette(out, {"strength": float(p.get("vignette_amount", 0.35))})
    return as_rgb(out)


def cinematic_contrast(frame: Any, params: dict[str, Any] | None = None) -> np.ndarray:
    """Teal-and-orange-ish contrast grade (lights warm / darks cool)."""
    p = params or {}
    img = as_rgb(frame).astype(np.float32) / 255.0
    contrast = float(p.get("contrast", 1.18))
    saturation = float(p.get("saturation", 0.9))
    warm = float(p.get("warm_highlights", 0.06))
    cool = float(p.get("cool_shadows", 0.05))
    mean = img.mean(axis=(0, 1), keepdims=True)
    lifted = (img - mean) * contrast + mean
    luma = lifted.mean(axis=-1, keepdims=True)
    out = luma + (lifted - luma) * saturation
    out = out.astype(np.float64)
    out += (0.0, warm * 0.5, warm * 0.35)
    out -= (cool * 0.3, cool * 0.2, 0.0)
    return (np.clip(out, 0.0, 1.0) * 255.0).astype(np.uint8)


def letterbox(frame: Any, params: dict[str, Any] | None = None) -> np.ndarray:
    """Letterbox the frame to a given aspect ratio (pillarbox-safe)."""
    p = params or {}
    aspect_ratio = float(p.get("aspect_ratio", 2.39))
    out = as_rgb(frame).astype(np.float32) / 255.0
    h, w = out.shape[:2]
    current = w / h
    if current > aspect_ratio:  # pillarbox sides
        bar_w = int((w - h * aspect_ratio) / 2)
        if bar_w > 0:
            out[:, :bar_w] = 0.0
            out[:, -bar_w:] = 0.0
    elif current < aspect_ratio:  # letterbox top/bottom
        bar_h = int((h - w / aspect_ratio) / 2)
        if bar_h > 0:
            out[:bar_h] = 0.0
            out[-bar_h:] = 0.0
    return (np.clip(out, 0.0, 1.0) * 255.0).astype(np.uint8)


def night_look(frame: Any, params: dict[str, Any] | None = None) -> np.ndarray:
    """Night scene grade: darken, cool it, add a strong vignette."""
    p = params or {}
    img = as_rgb(frame).astype(np.float32) / 255.0
    darkness = float(p.get("darkness", 0.55))
    blue_shift = float(p.get("blue_shift", 0.12))
    out = img * darkness
    out[..., 0] += blue_shift * 0.4
    out[..., 1] += blue_shift * 0.6
    out[..., 2] += blue_shift
    out = np.clip(out, 0.0, 1.0)
    return _vignette(out, {"strength": float(p.get("vignette_amount", 0.55))})


def golden_hour(frame: Any, params: dict[str, Any] | None = None) -> np.ndarray:
    """Golden hour grade: warm lift + soft low-angle flare."""
    p = params or {}
    img = as_rgb(frame).astype(np.float32) / 255.0
    warmth = float(p.get("warmth", 0.16))
    soft_glow = clamp(float(p.get("soft_glow", 0.3)), 0.0, 1.0)
    out = img.astype(np.float32)
    out[..., 0] *= 1.0 - warmth * 0.4
    out[..., 1] *= 1.0 - warmth * 0.1
    out[..., 2] *= 1.0 + warmth * 0.55
    out = np.clip(out, 0.0, 1.0)
    if soft_glow > 0:
        blurred = gaussian_blur(out, radius=max(1.0, 8.0 * soft_glow))
        out = out * (1 - soft_glow) + blurred * soft_glow
    out = _flare(
        out,
        {
            "x": 0.5,
            "y": 0.3,
            "strength": float(p.get("flare_strength", 0.25)),
            "color": [1.0, 190 / 255, 120 / 255],
        },
    )
    return as_rgb(out)


def film_look(frame: Any, params: dict[str, Any] | None = None) -> np.ndarray:
    """Classic film emulation: subtle grain + gentle contrast S-curve."""
    p = params or {}
    img = as_rgb(frame).astype(np.float32) / 255.0
    contrast = float(p.get("contrast", 0.1))
    pivot = img - 0.5
    graded = img + contrast * np.sin(np.pi * pivot) / np.pi
    graded = np.clip(graded, 0.0, 1.0)
    return _grain(graded, {"strength": float(p.get("grain", 0.06)), "seed": int(p.get("seed", 42))})


# Registry of presets (name -> callable)
CINEMATIC_PRESETS: dict[str, Any] = {
    "anamorphic": anamorphic_look,
    "cinematic_contrast": cinematic_contrast,
    "night": night_look,
    "golden_hour": golden_hour,
    "letterbox": letterbox,
    "film_look": film_look,
}
