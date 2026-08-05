"""Glow — soft bloom-like glow from the bright regions of the frame.

Brights are boosted, blurred and screen-blended over the original, producing
the dreamy HDR look. ``radius`` controls the halo size, ``intensity`` the mix.
"""
from __future__ import annotations

from typing import Any

import numpy as np

from modules.ai_video_studio.ai_effects.effects_engine import gaussian_blur, screen_blend
from modules.ai_video_studio.editor_common import as_rgb, clamp, make_logger

logger = make_logger("effects.glow")


def apply(frame: Any, params: dict[str, Any]) -> np.ndarray:
    img = as_rgb(frame).astype(np.float32) / 255.0
    intensity = clamp(float(params.get("intensity", 0.4)), 0.0, 1.0)
    radius = max(0.5, float(params.get("radius", 8.0)))
    threshold = float(params.get("threshold", 0.6))
    bright = np.clip(img - threshold, 0, 1) / max(1e-6, 1.0 - threshold)
    glow = gaussian_blur(bright, radius)
    out = screen_blend(img, glow * intensity)
    return (np.clip(out, 0, 1) * 255).astype(np.uint8)
