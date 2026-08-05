"""Animation sync — assigns animation styles to boards."""
from __future__ import annotations

from typing import Any


class AnimationSync:
    """Assigns animation/motion styles to boards."""

    STYLE_BY_TYPE = {
        "intro": "zoom-in",
        "opening": "pan",
        "presentation": "fade-in",
        "explanation": "step-reveal",
        "comparison": "split",
        "product": "rotate",
        "testimonial": "fade-in",
        "closing": "zoom-out",
        "credits": "scroll",
        "outro": "zoom-in",
    }

    def assign(self, boards: list[dict[str, Any]]) -> list[dict[str, Any]]:
        for board in boards:
            board["animation"] = self.STYLE_BY_TYPE.get(board.get("type", "presentation"), "fade-in")
        return boards


_animation_sync: AnimationSync | None = None


def get_animation_sync() -> AnimationSync:
    global _animation_sync
    if _animation_sync is None:
        _animation_sync = AnimationSync()
    return _animation_sync
