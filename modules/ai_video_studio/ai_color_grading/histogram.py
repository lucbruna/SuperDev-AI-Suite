"""Histogram — per-channel and luma histograms from a frame.

Returns 256-bin counts plus cumulative distribution, useful for exposing
clips, auto-exposure and validation.
"""
from __future__ import annotations

from typing import Any

import numpy as np

from modules.ai_video_studio.ai_color_grading.grading_engine import to_float01
from modules.ai_video_studio.editor_common import make_logger

logger = make_logger("color.histogram")


class Histogram:
    def compute(self, frame: Any, bins: int = 256) -> dict[str, Any]:
        img = to_float01(frame)
        hist = {}
        for i, ch in enumerate("rgb"):
            values, _ = np.histogram(img[..., i], bins=bins, range=(0.0, 1.0))
            hist[ch] = values.tolist()
        luma = img @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
        values, _ = np.histogram(luma, bins=bins, range=(0.0, 1.0))
        hist["luma"] = values.tolist()
        hist["bins"] = bins
        return hist

    def percentile(self, frame: Any, pct: float) -> float:
        luma = to_float01(frame) @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
        return float(np.percentile(luma, pct))
