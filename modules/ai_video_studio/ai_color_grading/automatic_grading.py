"""Automatic grading — auto exposure and auto white balance from statistics.

``auto_exposure`` stretches the luma histogram between percentile anchors so
mid-tones land near the middle. ``auto_white_balance`` applies the gray-world
assumption: each channel is scaled so its mean matches the overall mean.
"""
from __future__ import annotations

import numpy as np

from modules.ai_video_studio.ai_color_grading.grading_engine import to_float01
from modules.ai_video_studio.editor_common import make_logger

logger = make_logger("color.auto")


class AutomaticGrading:
    def auto_exposure(self, frame: any, lo_pct: float = 0.02, hi_pct: float = 0.98) -> float:
        """Return exposure adjustment (stops) that centers the luma range."""
        img = to_float01(frame)
        luma = img @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
        lo = np.percentile(luma, lo_pct * 100)
        hi = np.percentile(luma, hi_pct * 100)
        span = max(1e-6, hi - lo)
        target_span = 0.75
        scale = target_span / span
        return float(np.log2(scale))

    def auto_white_balance(self, frame: any) -> dict[str, float]:
        """Gray-world per-channel gains (mean-matched to the luma mean)."""
        img = to_float01(frame)
        means = img.reshape(-1, 3).mean(axis=0)
        target = means.mean()
        gains = {}
        for channel, mean in zip(("r", "g", "b"), means):
            gains[channel] = float(np.clip(target / max(1e-6, mean), 0.1, 10.0))
        return gains

    def grade(self, frame: any) -> dict[str, object]:
        """Apply both suggestions and return the pipeline parameters."""
        return {
            "exposure": self.auto_exposure(frame),
            "white_balance": self.auto_white_balance(frame),
        }
