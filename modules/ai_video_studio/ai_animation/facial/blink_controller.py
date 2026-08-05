"""Blink controller — schedule and animate eye blinks."""
from __future__ import annotations

import math
from typing import Any


class BlinkController:
    """Produces blink events with typical human cadence."""

    def schedule(self, total_frames: int, *, fps: int = 24) -> list[dict[str, Any]]:
        blinks: list[dict[str, Any]] = []
        interval = int(fps * 4)  # ~4 seconds between blinks
        frame = interval
        while frame < total_frames:
            blinks.append({"frame": frame, "duration": 6})
            frame += interval
        return blinks

    def blink_amount(self, frame: int, blink: dict[str, Any]) -> float:
        local = frame - blink["frame"]
        if local < 0 or local > blink["duration"]:
            return 0.0
        # 0 → fully closed → 0 over the blink duration.
        return abs(math.sin(math.pi * local / blink["duration"]))
