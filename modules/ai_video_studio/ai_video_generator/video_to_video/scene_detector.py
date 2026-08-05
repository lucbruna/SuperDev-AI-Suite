"""Scene detector — find scene boundaries within a video."""
from __future__ import annotations

from typing import Any


class SceneDetector:
    """Detects cuts and scene changes by frame-difference heuristics."""

    def detect(self, frames: list[dict[str, Any]], *, sensitivity: float = 0.5) -> dict[str, Any]:
        cuts: list[int] = []
        for i in range(1, len(frames)):
            # Deterministic pseudo-difference based on seed variation.
            diff = abs(frames[i].get("seed", 0) - frames[i - 1].get("seed", 0)) / (2**32)
            if diff > sensitivity:
                cuts.append(frames[i]["index"])
        return {"scene_boundaries": cuts, "scene_count": len(cuts) + 1, "sensitivity": sensitivity}
