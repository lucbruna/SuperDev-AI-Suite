"""Video refiner — clean up the final animated sequence."""
from __future__ import annotations

from typing import Any


class VideoRefiner:
    """Applies post-processing passes to the generated sequence."""

    _PASSES = ("denoise", "sharpen", "color_grade", "stabilize")

    def refine(self, frames: list[dict[str, Any]], *, passes: list[str] | None = None) -> dict[str, Any]:
        passes = passes or ["denoise", "color_grade"]
        unknown = [p for p in passes if p not in self._PASSES]
        if unknown:
            raise ValueError(f"Unknown refinement passes: {unknown}")
        return {
            "frames_processed": len(frames),
            "passes": list(passes),
            "refined_frames": list(frames),
        }

    def available_passes(self) -> list[str]:
        return list(self._PASSES)
