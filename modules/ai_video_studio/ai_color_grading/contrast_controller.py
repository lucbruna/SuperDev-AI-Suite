"""Contrast controller — S-curve and pivot-based contrast adjustment."""
from __future__ import annotations

from typing import Any

import numpy as np

from modules.ai_video_studio.ai_color_grading.grading_engine import to_float01
from modules.ai_video_studio.editor_common import make_logger

logger = make_logger("color.contrast")


class ContrastController:
    def apply(self, frame: Any, amount: float, pivot: float = 0.5) -> np.ndarray:
        """Contrast around ``pivot``: f(x) = pivot + (x - pivot) * (1 + amount)."""
        img = to_float01(frame)
        out = pivot + (img - pivot) * (1.0 + amount)
        return (np.clip(out, 0, 1) * 255.0).astype(np.uint8)

    def s_curve(self, frame: Any, amount: float) -> np.ndarray:
        """Sigmoid-style curve: lifts mid-tones, deepens shadows/highlights."""
        img = to_float01(frame)
        pivot = img - 0.5
        out = img + amount * np.sin(np.pi * pivot) / np.pi
        return (np.clip(out, 0, 1) * 255.0).astype(np.uint8)
