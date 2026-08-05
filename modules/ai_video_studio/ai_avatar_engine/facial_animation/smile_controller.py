"""Smile controller — smile and mouth-corner deltas."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.editor_common import clamp


class SmileController:
    """Produces smile parameters."""

    def drive(self, *, amount: float = 0.0) -> dict[str, Any]:
        amount = clamp(amount, -1.0, 1.0)
        return {
            "smile": amount,
            "cheek_raise": max(0.0, amount) * 0.6,
            "mouth_width": abs(amount) * 0.5,
        }


_smile_controller: SmileController | None = None


def get_smile_controller() -> SmileController:
    global _smile_controller
    if _smile_controller is None:
        _smile_controller = SmileController()
    return _smile_controller
