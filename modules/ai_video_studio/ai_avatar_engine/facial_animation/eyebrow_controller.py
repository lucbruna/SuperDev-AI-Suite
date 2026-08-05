"""Eyebrow controller — brow raise/frown/inner deltas."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.editor_common import clamp


class EyebrowController:
    """Produces eyebrow parameters."""

    def drive(self, *, raise_level: float = 0.0, frown: float = 0.0,
              inner: float = 0.0) -> dict[str, Any]:
        return {
            "brow_raise": clamp(raise_level, 0.0, 1.0),
            "brow_frown": clamp(frown, 0.0, 1.0),
            "brow_inner": clamp(inner, -1.0, 1.0),
        }


_eyebrow_controller: EyebrowController | None = None


def get_eyebrow_controller() -> EyebrowController:
    global _eyebrow_controller
    if _eyebrow_controller is None:
        _eyebrow_controller = EyebrowController()
    return _eyebrow_controller
