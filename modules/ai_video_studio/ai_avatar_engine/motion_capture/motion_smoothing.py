"""Motion smoothing — temporal smoothing of keypoint streams."""
from __future__ import annotations


import numpy as np


class MotionSmoothing:
    """Applies a moving-average (or exponential) smooth to joint streams."""

    def smooth(self, frames: list[dict[str, tuple[float, float]]],
               *, strength: float = 0.5, mode: str = "moving") -> list[dict[str, tuple[float, float]]]:
        if not frames:
            return []
        strength = max(0.0, min(1.0, strength))
        joints = sorted({j for frame in frames for j in frame})
        smoothed: list[dict[str, tuple[float, float]]] = []
        for i, frame in enumerate(frames):
            out: dict[str, tuple[float, float]] = {}
            for joint in joints:
                series = [f.get(joint) for f in frames[: i + 1]]
                series = [s for s in series if s is not None]
                if not series:
                    continue
                if mode == "exponential" and len(series) > 1:
                    alpha = 0.1 + strength * 0.6
                    pos = series[-1]
                    prev = series[-2]
                    x = alpha * pos[0] + (1 - alpha) * prev[0]
                    y = alpha * pos[1] + (1 - alpha) * prev[1]
                else:
                    xs = np.mean([s[0] for s in series[-5:]])
                    ys = np.mean([s[1] for s in series[-5:]])
                    x = xs
                    y = ys
                out[joint] = (round(float(x), 4), round(float(y), 4))
            smoothed.append(out)
        return smoothed


_motion_smoothing: MotionSmoothing | None = None


def get_motion_smoothing() -> MotionSmoothing:
    global _motion_smoothing
    if _motion_smoothing is None:
        _motion_smoothing = MotionSmoothing()
    return _motion_smoothing
