"""Motion cleaner — removes spikes/outliers from keypoint streams."""
from __future__ import annotations


import numpy as np


class MotionCleaner:
    """Filters outlier keypoints (median filter on per-joint positions)."""

    def clean(self, frames: list[dict[str, tuple[float, float]]],
              *, window: int = 3) -> list[dict[str, tuple[float, float]]]:
        if not frames:
            return []
        joints = sorted({j for frame in frames for j in frame})
        window = max(1, window | 1)
        cleaned: list[dict[str, tuple[float, float]]] = []
        for i, frame in enumerate(frames):
            out: dict[str, tuple[float, float]] = {}
            for joint in joints:
                series = [f.get(joint) for f in frames[max(0, i - window // 2): i + window // 2 + 1]]
                series = [s for s in series if s is not None]
                if not series:
                    continue
                xs = np.median([s[0] for s in series])
                ys = np.median([s[1] for s in series])
                out[joint] = (round(float(xs), 4), round(float(ys), 4))
            cleaned.append(out)
        return cleaned


_motion_cleaner: MotionCleaner | None = None


def get_motion_cleaner() -> MotionCleaner:
    global _motion_cleaner
    if _motion_cleaner is None:
        _motion_cleaner = MotionCleaner()
    return _motion_cleaner
