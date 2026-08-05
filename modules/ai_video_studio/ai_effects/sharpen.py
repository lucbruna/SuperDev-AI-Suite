"""Sharpen — unsharp mask applied to the luma channel.

A blurred copy is subtracted from the original scaled by ``amount``; only the
luma is sharpened so color edges do not ring as much.
"""
from __future__ import annotations

from typing import Any

import numpy as np

from modules.ai_video_studio.ai_effects.effects_engine import gaussian_blur
from modules.ai_video_studio.editor_common import as_rgb, clamp, make_logger

_LUMA = np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)

logger = make_logger("effects.sharpen")


def apply(frame: Any, params: dict[str, Any]) -> np.ndarray:
    img = as_rgb(frame).astype(np.float32) / 255.0
    amount = clamp(float(params.get("amount", 0.6)), 0.0, 2.0)
    radius = max(0.5, float(params.get("radius", 1.0)))
    luma = img @ _LUMA
    blurred = gaussian_blur(img, radius)
    blur_luma = blurred @ _LUMA
    sharpening = (luma - blur_luma) * amount
    out = img + sharpening[..., None]
    return (np.clip(out, 0, 1) * 255).astype(np.uint8)
