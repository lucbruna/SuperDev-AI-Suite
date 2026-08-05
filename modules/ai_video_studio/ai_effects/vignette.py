"""Vignette — radial falloff darkening toward the corners."""
from __future__ import annotations

from typing import Any

import numpy as np

from modules.ai_video_studio.editor_common import as_rgb, clamp, make_logger

logger = make_logger("effects.vignette")


def apply(frame: Any, params: dict[str, Any]) -> np.ndarray:
    img = as_rgb(frame).astype(np.float32) / 255.0
    h, w = img.shape[:2]
    strength = clamp(float(params.get("strength", 0.4)), 0.0, 1.0)
    inner = float(params.get("inner", 0.6))
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    nx = (xx / max(w - 1, 1)) * 2 - 1
    ny = (yy / max(h - 1, 1)) * 2 - 1
    dist = np.sqrt(nx * nx + ny * ny) / np.sqrt(2.0)
    mask = np.clip((dist - inner) / (1.0 - inner + 1e-6), 0.0, 1.0)
    darken = 1.0 - strength * mask
    out = img * darken[..., None]
    return (np.clip(out, 0, 1) * 255).astype(np.uint8)
