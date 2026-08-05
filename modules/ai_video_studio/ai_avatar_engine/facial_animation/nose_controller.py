"""Nose controller — nose-wrinkle deltas (disgust etc.)."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.editor_common import clamp


class NoseController:
    """Produces nose-wrinkle parameters."""

    def drive(self, *, wrinkle: float = 0.0) -> dict[str, Any]:
        return {"nose_wrinkle": clamp(wrinkle, 0.0, 1.0)}


_nose_controller: NoseController | None = None


def get_nose_controller() -> NoseController:
    global _nose_controller
    if _nose_controller is None:
        _nose_controller = NoseController()
    return _nose_controller
