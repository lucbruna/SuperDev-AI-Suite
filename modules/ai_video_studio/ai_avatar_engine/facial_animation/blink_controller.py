"""Blink controller — eyelid-closure deltas with natural blink timing."""
from __future__ import annotations

import math
from typing import Any

from modules.ai_video_studio.editor_common import clamp


class BlinkController:
    """Produces blink parameters; drives periodic natural blinks."""

    def __init__(self, blink_interval_s: float = 3.5, blink_duration_s: float = 0.15) -> None:
        self.interval = blink_interval_s
        self.duration = blink_duration_s

    def drive(self, *, t: float = 0.0, forced: float = 0.0) -> dict[str, Any]:
        """Return blink deltas at time ``t`` (seconds)."""
        phase = (t % self.interval) / max(self.interval, 1e-6)
        normal = math.exp(-((phase - 0.5) / 0.12) ** 2) * 0.08  # subtle periodic blink
        level = clamp(max(normal, forced), 0.0, 1.0)
        return {"blink_left": level, "blink_right": level}


_blink_controller: BlinkController | None = None


def get_blink_controller() -> BlinkController:
    global _blink_controller
    if _blink_controller is None:
        _blink_controller = BlinkController()
    return _blink_controller
