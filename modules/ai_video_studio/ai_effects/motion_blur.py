"""Motion blur — directional blur by accumulating shifted copies.

``angle`` (radians) and ``samples`` control the smear direction and quality;
the frame is translated along the direction and averaged. Deterministic.
"""
from __future__ import annotations

import math
from typing import Any

import numpy as np

from modules.ai_video_studio.editor_common import as_rgb, clamp, make_logger

logger = make_logger("effects.motionblur")


def apply(frame: Any, params: dict[str, Any]) -> np.ndarray:
    img = as_rgb(frame).astype(np.float32) / 255.0
    angle = float(params.get("angle", 0.0))
    distance = max(0.0, float(params.get("distance", 8.0)))
    samples = max(1, int(params.get("samples", 8)))
    if distance <= 0 or samples <= 1:
        return frame if isinstance(frame, np.ndarray) else as_rgb(frame)
    dx = math.cos(angle) * distance
    dy = math.sin(angle) * distance
    h, w = img.shape[:2]
    acc = np.zeros_like(img)
    count = 0
    for i in range(samples):
        t = -0.5 + i / (samples - 1)
        shift_x = int(round(dx * t))
        shift_y = int(round(dy * t))
        shifted = np.zeros_like(img)
        xs = slice(max(0, -shift_x), min(w, w - shift_x))
        ys = slice(max(0, -shift_y), min(h, h - shift_y))
        target_xs = slice(max(0, shift_x), min(w, w + shift_x))
        target_ys = slice(max(0, shift_y), min(h, h + shift_y))
        shifted[target_ys, target_xs] = img[ys, xs]
        acc += shifted
        count += 1
    out = acc / count
    return (np.clip(out, 0, 1) * 255).astype(np.uint8)
