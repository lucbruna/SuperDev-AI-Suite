"""Bloom — classic threshold → blur → add pipeline for highlights."""
from __future__ import annotations

from typing import Any

import numpy as np

from modules.ai_video_studio.ai_effects.effects_engine import gaussian_blur, linear_dodge
from modules.ai_video_studio.editor_common import as_rgb, clamp, make_logger

logger = make_logger("effects.bloom")


def apply(frame: Any, params: dict[str, Any]) -> np.ndarray:
    img = as_rgb(frame).astype(np.float32) / 255.0
    intensity = clamp(float(params.get("intensity", 0.5)), 0.0, 2.0)
    radius = max(0.5, float(params.get("radius", 6.0)))
    threshold = float(params.get("threshold", 0.7))
    bright = np.clip(img - threshold, 0, 1)
    bloom = gaussian_blur(bright, radius) * intensity
    out = linear_dodge(img, bloom)
    return (np.clip(out, 0, 1) * 255).astype(np.uint8)
