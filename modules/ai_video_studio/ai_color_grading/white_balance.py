"""White balance — gray-world and sampled-point corrections."""
from __future__ import annotations

from typing import Any

import numpy as np

from modules.ai_video_studio.ai_color_grading.grading_engine import to_float01
from modules.ai_video_studio.editor_common import make_logger

logger = make_logger("color.wb")


class WhiteBalance:
    def gray_world(self, frame: Any) -> dict[str, float]:
        """Scale channels so their means match (classic gray-world)."""
        img = to_float01(frame).reshape(-1, 3)
        means = img.mean(axis=0)
        target = means.mean()
        return {
            channel: float(np.clip(target / max(1e-6, m), 0.1, 10.0))
            for channel, m in zip(("r", "g", "b"), means)
        }

    def from_point(self, frame: Any, x: int, y: int) -> dict[str, float]:
        """White balance so the sampled pixel becomes neutral gray."""
        img = to_float01(frame)
        h, w = img.shape[:2]
        x, y = int(np.clip(x, 0, w - 1)), int(np.clip(y, 0, h - 1))
        px = img[y, x]
        target = px.mean()
        return {
            channel: float(np.clip(target / max(1e-6, v), 0.1, 10.0))
            for channel, v in zip(("r", "g", "b"), px)
        }

    def apply(self, frame: Any, gains: dict[str, float]) -> np.ndarray:
        img = to_float01(frame)
        img = img * np.array([gains.get("r", 1.0), gains.get("g", 1.0), gains.get("b", 1.0)], dtype=np.float32)
        return (np.clip(img, 0, 1) * 255.0).astype(np.uint8)
