"""Exposure controller — linear exposure adjustment in stops."""
from __future__ import annotations

from typing import Any

import numpy as np

from modules.ai_video_studio.ai_color_grading.grading_engine import to_float01
from modules.ai_video_studio.editor_common import make_logger

logger = make_logger("color.exposure")


class ExposureController:
    def apply(self, frame: Any, stops: float) -> np.ndarray:
        """Multiply pixel values by 2^stops (clipped to display range)."""
        img = to_float01(frame) * (2.0 ** stops)
        return (np.clip(img, 0, 1) * 255.0).astype(np.uint8)

    def auto(self, frame: Any) -> np.ndarray:
        """Apply an auto exposure that centers mid-tones (percentile-based)."""
        from modules.ai_video_studio.ai_color_grading.automatic_grading import AutomaticGrading

        stops = AutomaticGrading().auto_exposure(frame)
        return self.apply(frame, stops)
