"""Frame-level transitions shared by the DARKSTUDIO render pipeline."""
from __future__ import annotations

from typing import Any

import numpy as np


def transition_spec(scene: dict[str, Any]) -> dict[str, Any]:
    raw = scene.get("transition_out") or {}
    if not isinstance(raw, dict):
        raise ValueError("transition_out must be an object")
    kind = str(raw.get("type", "cut")).lower()
    if kind not in {"cut", "crossfade", "fade_through_black"}:
        raise ValueError(f"Unsupported transition type '{kind}'")
    frames = int(raw.get("duration_frames", 0))
    if kind == "cut":
        frames = 0
    elif frames < 2:
        raise ValueError("transition duration_frames must be at least 2")
    return {"type": kind, "duration_frames": frames}


def blend_frames(outgoing: np.ndarray, incoming: np.ndarray, alpha: float) -> np.ndarray:
    """Blend two same-sized RGB frames; alpha=1 selects the incoming frame."""
    a = np.asarray(outgoing, dtype=np.float32)
    b = np.asarray(incoming, dtype=np.float32)
    if a.shape != b.shape or a.ndim != 3 or a.shape[2] != 3:
        raise ValueError("Transition frames must have identical (height, width, 3) shapes")
    if not 0.0 <= alpha <= 1.0:
        raise ValueError("Transition alpha must be between zero and one")
    return np.clip(np.rint(a * (1.0 - alpha) + b * alpha), 0, 255).astype(np.uint8)


def fade_from_black(frame: np.ndarray, progress: float) -> np.ndarray:
    """Reveal a frame from black, with progress in [0, 1]."""
    return blend_frames(np.zeros_like(frame), frame, progress)


def fade_to_black(frame: np.ndarray, progress: float) -> np.ndarray:
    """Fade a frame to black, with progress in [0, 1]."""
    return blend_frames(frame, np.zeros_like(frame), progress)
