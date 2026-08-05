"""Curves editor — point-based master and per-channel curves.

A curve is a list of ``(x, y)`` control points; the editor builds a 256-entry
lookup per channel by linear interpolation between points and applies it to
the frame. The classic "S" and "fade" curves are provided as helpers.
"""
from __future__ import annotations

from typing import Any, Sequence

import numpy as np

from modules.ai_video_studio.ai_color_grading.grading_engine import to_float01
from modules.ai_video_studio.editor_common import make_logger

logger = make_logger("color.curves")


def _build_lut(points: Sequence[tuple[float, float]]) -> np.ndarray:
    pts = sorted((max(0.0, min(1.0, x)), max(0.0, min(1.0, y))) for x, y in points)
    if len(pts) < 2:
        pts = [(0.0, 0.0), (1.0, 1.0)]
    xs = np.array([p[0] for p in pts], dtype=np.float32)
    ys = np.array([p[1] for p in pts], dtype=np.float32)
    positions = np.linspace(0.0, 1.0, 256, dtype=np.float32)
    return np.interp(positions, xs, ys).astype(np.float32)


class CurvesEditor:
    def __init__(self) -> None:
        self.master: list[tuple[float, float]] = [(0.0, 0.0), (1.0, 1.0)]
        self.channels: dict[str, list[tuple[float, float]]] = {}

    def set_master(self, points: Sequence[tuple[float, float]]) -> None:
        self.master = list(points)

    def set_channel(self, channel: str, points: Sequence[tuple[float, float]]) -> None:
        if channel not in {"r", "g", "b"}:
            raise ValueError("channel must be one of 'r', 'g', 'b'")
        self.channels[channel] = list(points)

    def apply(self, frame: Any) -> np.ndarray:
        img = to_float01(frame)
        out = img.copy()
        master = _build_lut(self.master)
        for c, key in enumerate("rgb"):
            lut = _build_lut(self.channels.get(key, [(0.0, 0.0), (1.0, 1.0)]))
            x = (out[..., c] * 255.0).astype(np.int32)
            x = np.clip(x, 0, 255)
            out[..., c] = master[x] * lut[x]
        return (np.clip(out, 0, 1) * 255.0).astype(np.uint8)

    @staticmethod
    def s_curve(strength: float = 1.0) -> list[tuple[float, float]]:
        return [(0.0, 0.0), (0.25, 0.15 * strength), (0.5, 0.5), (0.75, 0.85 * strength), (1.0, 1.0)]

    @staticmethod
    def fade(amount: float = 0.1) -> list[tuple[float, float]]:
        return [(0.0, amount), (1.0, 1.0 - amount)]
