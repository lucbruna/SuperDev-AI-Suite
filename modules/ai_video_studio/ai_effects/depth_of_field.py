"""Depth of field — simulated shallow DoF via radial/edge blur.

A focal point stays sharp while regions away from it are blurred with a
strength that grows with distance (radial blur approximation using box-blur
strength modulated by a focus mask).
"""
from __future__ import annotations

from typing import Any

import numpy as np

from modules.ai_video_studio.ai_effects.effects_engine import box_blur
from modules.ai_video_studio.editor_common import as_rgb, clamp, make_logger

logger = make_logger("effects.dof")


def apply(frame: Any, params: dict[str, Any]) -> np.ndarray:
    img = as_rgb(frame).astype(np.float32) / 255.0
    h, w = img.shape[:2]
    fx = float(params.get("focus_x", 0.5)) * w
    fy = float(params.get("focus_y", 0.5)) * h
    strength = max(0.0, float(params.get("strength", 0.5)))
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dist = np.sqrt((xx - fx) ** 2 + (yy - fy) ** 2) / max(0.1 * max(w, h), 1.0)
    mask = np.clip((dist - 0.4) / 0.8, 0.0, 1.0)
    blurred = box_blur(img, max(1, int(4 + 12 * strength)))
    out = img * (1 - mask[..., None]) + blurred * mask[..., None]
    return (np.clip(out, 0, 1) * 255).astype(np.uint8)
