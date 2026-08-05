"""Denoise — edge-preserving smoothing.

Approximates a bilateral filter by blurring the image and blending back the
original where the local contrast is high (edges), preserving detail while
smoothing flat regions.
"""
from __future__ import annotations

from typing import Any

import numpy as np

from modules.ai_video_studio.ai_effects.effects_engine import gaussian_blur
from modules.ai_video_studio.editor_common import as_rgb, clamp, make_logger

logger = make_logger("effects.denoise")


def apply(frame: Any, params: dict[str, Any]) -> np.ndarray:
    img = as_rgb(frame).astype(np.float32) / 255.0
    strength = clamp(float(params.get("strength", 0.5)), 0.0, 1.0)
    radius = max(0.5, float(params.get("radius", 2.0)))
    edge = float(params.get("edge_threshold", 0.12))
    blurred = gaussian_blur(img, radius)
    detail = np.abs(img - blurred)
    edge_mask = np.clip(detail / edge, 0.0, 1.0)  # 1 = keep original
    out = img * edge_mask * strength + blurred * (1.0 - edge_mask * strength)
    return (np.clip(out, 0, 1) * 255).astype(np.uint8)
