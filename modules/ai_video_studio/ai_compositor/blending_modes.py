"""Blending modes used across compositing, color and effects subsystems."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def _prep(a: NDArray[np.floating], b: NDArray[np.floating]) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    return a.astype(np.float64), b.astype(np.float64)


def blend(
    base: NDArray[np.floating],
    overlay: NDArray[np.floating],
    *,
    mode: str = "normal",
    amount: float = 1.0,
) -> NDArray[np.floating]:
    """Blend ``overlay`` onto ``base`` with ``mode`` at ``amount`` opacity."""
    a, b = _prep(base, overlay)
    if b.shape != a.shape:
        b = np.resize(b, a.shape)
    if mode == "normal":
        out = a * (1 - amount) + b * amount
    elif mode == "multiply":
        out = a * b
        out = a * (1 - amount) + out * amount
    elif mode == "screen":
        out = 1 - (1 - a) * (1 - b)
        out = a * (1 - amount) + out * amount
    elif mode == "overlay":
        low = 2 * a * b
        high = 1 - 2 * (1 - a) * (1 - b)
        out = np.where(a < 0.5, low, high)
        out = a * (1 - amount) + out * amount
    elif mode == "soft_light":
        out = (1 - 2 * b) * a**2 + 2 * b * a
        out = a * (1 - amount) + out * amount
    elif mode == "darken":
        out = np.minimum(a, b)
        out = a * (1 - amount) + out * amount
    elif mode == "lighten":
        out = np.maximum(a, b)
        out = a * (1 - amount) + out * amount
    elif mode == "color_dodge":
        denom = 1 - b
        out = np.where(denom <= 0, 1.0, a / denom)
        out = np.clip(a * (1 - amount) + out * amount, 0.0, 1.0)
    elif mode == "color_burn":
        denom = b + 1e-8
        out = 1 - (1 - a) / denom
        out = np.clip(a * (1 - amount) + out * amount, 0.0, 1.0)
    elif mode == "difference":
        out = np.abs(a - b)
        out = a * (1 - amount) + out * amount
    elif mode == "add":
        out = a + b
        out = np.clip(a * (1 - amount) + out * amount, 0.0, 1.0)
    elif mode == "subtract":
        out = np.clip(a - b, 0.0, 1.0)
        out = a * (1 - amount) + out * amount
    else:
        raise ValueError(f"unknown blend mode {mode!r}")
    return np.clip(out, 0.0, 1.0)


BLEND_MODES: tuple[str, ...] = (
    "normal",
    "multiply",
    "screen",
    "overlay",
    "soft_light",
    "darken",
    "lighten",
    "color_dodge",
    "color_burn",
    "difference",
    "add",
    "subtract",
)


def blend_modes() -> tuple[str, ...]:
    return BLEND_MODES
