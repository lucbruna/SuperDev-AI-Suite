"""Movement classifier — labels motion as walk/run/jump/idle/etc."""
from __future__ import annotations

from typing import Any

import numpy as np


class MovementClassifier:
    """Classifies a sequence of hip positions into a movement label."""

    def classify(self, hips: list[tuple[float, float]], *, fps: int = 24) -> str:
        if len(hips) < 3:
            return "idle"
        pts = np.asarray(hips, dtype=np.float64)
        speeds = np.linalg.norm(np.diff(pts, axis=0), axis=1)
        avg_speed = float(np.mean(speeds) * fps)  # normalized units per second
        vertical = float(np.max(pts[:, 1]) - np.min(pts[:, 1]))
        if avg_speed < 0.03 and vertical < 0.05:
            return "idle"
        if vertical > 0.15:
            return "jump"
        if avg_speed > 0.3:
            return "run"
        return "walk"

    def label(self, motion: list[dict[str, Any]]) -> str:
        hips = [tuple(m.get("hip", (0.5, 0.5))) for m in motion]
        return self.classify(hips)


_movement_classifier: MovementClassifier | None = None


def get_movement_classifier() -> MovementClassifier:
    global _movement_classifier
    if _movement_classifier is None:
        _movement_classifier = MovementClassifier()
    return _movement_classifier
