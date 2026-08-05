"""Jaw controller — jaw openness deltas."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.editor_common import clamp


class JawController:
    """Produces jaw/mouth-open parameters."""

    def drive(self, *, open: float = 0.0) -> dict[str, Any]:
        open = clamp(open, 0.0, 1.0)
        return {"jaw_open": open, "mouth_open": open}


_jaw_controller: JawController | None = None


def get_jaw_controller() -> JawController:
    global _jaw_controller
    if _jaw_controller is None:
        _jaw_controller = JawController()
    return _jaw_controller
