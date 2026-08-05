"""Color wheels — per-channel lift / gamma / gain adjustments.

Mirrors the classic color-wheel controls: lift shifts shadows, gamma curves
mid-tones, gain scales highlights. Each is applied per RGB channel.
"""
from __future__ import annotations

from typing import Any

import numpy as np

from modules.ai_video_studio.ai_color_grading.grading_engine import to_float01
from modules.ai_video_studio.editor_common import make_logger

logger = make_logger("color.wheels")


class ColorWheels:
    def __init__(self) -> None:
        self.lift: dict[str, float] = {"r": 0.0, "g": 0.0, "b": 0.0}
        self.gamma: dict[str, float] = {"r": 1.0, "g": 1.0, "b": 1.0}
        self.gain: dict[str, float] = {"r": 1.0, "g": 1.0, "b": 1.0}

    def apply(self, frame: Any) -> np.ndarray:
        img = to_float01(frame)
        out = img.copy()
        for i, ch in enumerate("rgb"):
            out[..., i] = np.clip((out[..., i] + self.lift[ch]) ** self.gamma[ch] * self.gain[ch], 0.0, 1.0)
        return (out * 255.0).astype(np.uint8)

    def reset(self) -> None:
        self.lift = {"r": 0.0, "g": 0.0, "b": 0.0}
        self.gamma = {"r": 1.0, "g": 1.0, "b": 1.0}
        self.gain = {"r": 1.0, "g": 1.0, "b": 1.0}

    def as_dict(self) -> dict[str, dict[str, float]]:
        return {"lift": dict(self.lift), "gamma": dict(self.gamma), "gain": dict(self.gain)}
