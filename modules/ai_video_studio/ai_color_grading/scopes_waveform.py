"""Waveform scope — luma/RGB brightness vs. horizontal position.

Downsamples the frame to a small column count and returns per-column luma
(min/max/mean) so the scope can be drawn as the classic oscilloscope trace.
"""
from __future__ import annotations

from typing import Any

import numpy as np

from modules.ai_video_studio.ai_color_grading.grading_engine import to_float01
from modules.ai_video_studio.editor_common import make_logger

logger = make_logger("color.waveform")


class ScopesWaveform:
    def compute(self, frame: Any, columns: int = 128, channel: str = "luma") -> dict[str, Any]:
        img = to_float01(frame)
        h, w = img.shape[:2]
        col_idx = (np.linspace(0, w - 1, columns)).astype(int)
        if channel == "luma":
            data = img @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
        else:
            data = img[..., "rgb".index(channel)]
        cols = data[:, col_idx]
        return {
            "columns": columns,
            "channel": channel,
            "min": np.min(cols, axis=0).tolist(),
            "max": np.max(cols, axis=0).tolist(),
            "mean": np.mean(cols, axis=0).tolist(),
        }
