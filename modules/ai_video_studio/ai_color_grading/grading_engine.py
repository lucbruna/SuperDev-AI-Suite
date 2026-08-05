"""Grading engine — real per-frame color grading pipeline.

The pipeline operates on float [0, 1] RGB and applies, in order:

1. white balance (per-channel gains)
2. exposure (linear multiplier)
3. lift / gamma / gain (per-channel)
4. temp / tint (channel offsets)
5. saturation (luma-preserving)
6. contrast S-curve
7. LUT (optional)
8. curves (optional, applied last)

Everything is pure numpy so grades are deterministic and testable.
"""
from __future__ import annotations

from typing import Any, Callable

import numpy as np

from modules.ai_video_studio.editor_common import as_rgb, clamp, make_logger

logger = make_logger("color.grade")


def to_float01(frame: Any) -> np.ndarray:
    return as_rgb(frame).astype(np.float32) / 255.0


def from_float01(arr: np.ndarray) -> np.ndarray:
    return np.clip(arr, 0.0, 1.0).astype(np.float32)


class GradePipeline:
    """Composable, ordered color-grading pipeline for a single frame."""

    def __init__(self) -> None:
        self.white_balance: dict[str, float] = {"r": 1.0, "g": 1.0, "b": 1.0}
        self.exposure = 0.0  # stops
        self.lift: tuple[float, float, float] = (0.0, 0.0, 0.0)
        self.gamma: tuple[float, float, float] = (1.0, 1.0, 1.0)
        self.gain: tuple[float, float, float] = (1.0, 1.0, 1.0)
        self.temp = 0.0  # negative = cooler, positive = warmer
        self.tint = 0.0  # negative = greener, positive = magenta
        self.saturation = 1.0
        self.contrast = 0.0  # -1..1
        self.lut: Callable[[np.ndarray], np.ndarray] | None = None
        self.curves: Callable[[np.ndarray], np.ndarray] | None = None

    def apply(self, frame: Any) -> np.ndarray:
        """Grade ``frame`` and return a uint8 HxWx3 result."""
        img = to_float01(frame)
        img = img * np.array(
            [self.white_balance["r"], self.white_balance["g"], self.white_balance["b"]], dtype=np.float32
        )
        if self.exposure:
            img = img * (2.0 ** self.exposure)
        img = self._lift_gamma_gain(img)
        if self.temp or self.tint:
            img = self._temp_tint(img)
        if self.saturation != 1.0:
            img = self._saturate(img, self.saturation)
        if self.contrast:
            img = self._contrast_curve(img, self.contrast)
        if self.lut is not None:
            img = from_float01(self.lut(from_float01(img)))
        if self.curves is not None:
            img = from_float01(self.curves(from_float01(img)))
        return (from_float01(img) * 255.0).astype(np.uint8)

    # ── Stage implementations ─────────────────────────────────────
    def _lift_gamma_gain(self, img: np.ndarray) -> np.ndarray:
        lr, lg, lb = self.lift
        gr, gg, gb = self.gamma
        nr, ng, nb = self.gain
        out = img.copy()
        # Clip the base to [0, 1] before the power to avoid NaN from
        # negative bases raised to a fractional gamma.
        out[..., 0] = np.clip(np.clip(out[..., 0] + lr, 0.0, 1.0) ** gr * nr, 0.0, 1.0)
        out[..., 1] = np.clip(np.clip(out[..., 1] + lg, 0.0, 1.0) ** gg * ng, 0.0, 1.0)
        out[..., 2] = np.clip(np.clip(out[..., 2] + lb, 0.0, 1.0) ** gb * nb, 0.0, 1.0)
        return out

    def _temp_tint(self, img: np.ndarray) -> np.ndarray:
        out = img.copy()
        if self.temp != 0:
            out[..., 0] += self.temp * 0.05
            out[..., 2] -= self.temp * 0.05
        if self.tint != 0:
            out[..., 1] += self.tint * 0.04
            out[..., 0] -= self.tint * 0.02
            out[..., 2] -= self.tint * 0.02
        return out

    @staticmethod
    def _saturate(img: np.ndarray, amount: float) -> np.ndarray:
        luma = img @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
        return luma[..., None] + (img - luma[..., None]) * amount

    @staticmethod
    def _contrast_curve(img: np.ndarray, amount: float) -> np.ndarray:
        # S-curve around 0.5: f(x) = x + amount * sin(pi * (x - 0.5)) / pi
        pivot = img - 0.5
        return img + amount * np.sin(np.pi * pivot) / np.pi

    def as_dict(self) -> dict[str, Any]:
        return {
            "white_balance": dict(self.white_balance),
            "exposure": self.exposure,
            "lift": list(self.lift),
            "gamma": list(self.gamma),
            "gain": list(self.gain),
            "temp": self.temp,
            "tint": self.tint,
            "saturation": self.saturation,
            "contrast": self.contrast,
        }
