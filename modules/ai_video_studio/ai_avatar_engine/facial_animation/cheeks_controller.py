"""Cheeks controller — cheek-raise deltas."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.editor_common import clamp


class CheeksController:
    """Produces cheek-raise parameters."""

    def drive(self, *, raise_level: float = 0.0) -> dict[str, Any]:
        return {"cheek_raise": clamp(raise_level, 0.0, 1.0)}


_cheeks_controller: CheeksController | None = None


def get_cheeks_controller() -> CheeksController:
    global _cheeks_controller
    if _cheeks_controller is None:
        _cheeks_controller = CheeksController()
    return _cheeks_controller
