"""Camera motion — apply synthetic camera movement over frames."""
from __future__ import annotations

from typing import Any

_MOTIONS = ("static", "pan_left", "pan_right", "zoom_in", "zoom_out", "tilt_up", "tilt_down")


class CameraMotion:
    """Computes camera transforms per frame index."""

    def transform(self, frame_index: int, total: int, *, motion: str = "static") -> dict[str, Any]:
        if motion not in _MOTIONS:
            motion = "static"
        t = frame_index / max(1, total - 1)
        base: dict[str, Any] = {"frame": frame_index, "motion": motion, "dx": 0.0, "dy": 0.0, "zoom": 1.0}
        if motion == "pan_left":
            base["dx"] = round(-t * 0.2, 4)
        elif motion == "pan_right":
            base["dx"] = round(t * 0.2, 4)
        elif motion == "zoom_in":
            base["zoom"] = round(1.0 + t * 0.15, 4)
        elif motion == "zoom_out":
            base["zoom"] = round(1.15 - t * 0.15, 4)
        elif motion == "tilt_up":
            base["dy"] = round(-t * 0.15, 4)
        elif motion == "tilt_down":
            base["dy"] = round(t * 0.15, 4)
        return base

    def path(self, total: int, *, motion: str = "static") -> list[dict[str, Any]]:
        return [self.transform(i, total, motion=motion) for i in range(total)]

    def available_motions(self) -> list[str]:
        return list(_MOTIONS)
