"""Stabilization engine — camera-path estimation + smoothing + frame warping.

Estimates frame-to-frame motion (phase correlation), smooths the path with
an exponential moving average, and warps frames back to the smoothed path.
The result is a stabilized frame with a slight crop to hide borders.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from numpy.typing import NDArray

from .camera_smoothing import smooth_trajectory


@dataclass
class StabilizeResult:
    frames: list[NDArray[np.floating]]
    path: np.ndarray
    smoothed: np.ndarray
    meta: dict[str, Any] = field(default_factory=dict)


class StabilizationEngine:
    """Deterministic video stabilization."""

    def __init__(self, smoothing: float = 0.6, crop_ratio: float = 0.08) -> None:
        self._smoothing = smoothing
        self._crop_ratio = crop_ratio

    def stabilize(self, frames: list[NDArray[np.floating]]) -> StabilizeResult:
        """Stabilize a list of frames (same shape). Returns warped frames."""
        if not frames:
            raise ValueError("no frames")
        h, w = frames[0].shape[:2]
        # 1. Estimate motion path (accumulate translations)
        path = np.zeros((len(frames), 2), dtype=np.float64)
        for i in range(1, len(frames)):
            dx, dy = self._estimate(frames[i - 1], frames[i])
            path[i] = path[i - 1] + (dx, dy)
        # 2. Smooth path
        smoothed = smooth_trajectory(path, alpha=self._smoothing)
        # 3. Warp each frame by the difference between smoothed and raw path
        crop = int(min(w, h) * self._crop_ratio)
        out: list[NDArray[np.floating]] = []
        for i, frame in enumerate(frames):
            dx = smoothed[i, 0] - path[i, 0]
            dy = smoothed[i, 1] - path[i, 1]
            out.append(_shift_clip(frame, dx, dy, crop))
        return StabilizeResult(frames=out, path=path, smoothed=smoothed)

    def _estimate(self, a: NDArray[np.floating], b: NDArray[np.floating]) -> tuple[float, float]:
        from ..ai_tracking.camera_tracking import CameraTracker

        tracker = CameraTracker()
        m = tracker.estimate(a, b)
        return float(m["dx"]), float(m["dy"])


def _shift_clip(frame: NDArray[np.floating], dx: float, dy: float, crop: int) -> NDArray[np.floating]:
    """Shift the frame by (dx, dy) and crop borders to hide empty edges."""
    f = frame.astype(np.float64)
    h, w = f.shape[:2]
    rolled = np.roll(np.roll(f, int(round(dy)), axis=0), int(round(dx)), axis=1)
    # Zero out the shifted-in edge sliver
    if dy > 0:
        rolled[: int(round(dy))] = 0
    elif dy < 0:
        rolled[int(round(dy)) :] = 0
    if dx > 0:
        rolled[:, : int(round(dx))] = 0
    elif dx < 0:
        rolled[:, int(round(dx)) :] = 0
    y0, y1 = crop, h - crop
    x0, x1 = crop, w - crop
    if y1 > y0 and x1 > x0:
        rolled = rolled[y0:y1, x0:x1]
    # Resize back to original size
    from ..editor_common import resize_frame

    return resize_frame(rolled, w, h)
