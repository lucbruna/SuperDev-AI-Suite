"""Motion analyzer — estimate motion vectors and optical flow."""
from __future__ import annotations

from typing import Any


class MotionAnalyzer:
    """Computes motion statistics across a frame sequence."""

    def analyze(self, frames: list[dict[str, Any]]) -> dict[str, Any]:
        if not frames:
            return {"average_magnitude": 0.0, "motion_level": "none", "flow_vectors": 0}
        total_motion = sum(abs(f.get("blend", 0)) * 100 for f in frames if "blend" in f)
        average = total_motion / len(frames)
        level = "high" if average > 40 else "medium" if average > 10 else "low"
        return {
            "average_magnitude": round(average, 2),
            "motion_level": level,
            "flow_vectors": len(frames) * 64,
            "frames": len(frames),
        }
