"""Forehead controller — forehead-raise deltas (surprise)."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.editor_common import clamp


class ForeheadController:
    """Produces forehead-raise parameters."""

    def drive(self, *, raise_level: float = 0.0) -> dict[str, Any]:
        return {"forehead_raise": clamp(raise_level, 0.0, 1.0)}


_forehead_controller: ForeheadController | None = None


def get_forehead_controller() -> ForeheadController:
    global _forehead_controller
    if _forehead_controller is None:
        _forehead_controller = ForeheadController()
    return _forehead_controller
