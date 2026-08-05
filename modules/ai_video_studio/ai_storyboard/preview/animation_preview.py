"""Animation preview — describes animation preview for a board."""
from __future__ import annotations

from typing import Any


class AnimationPreview:
    """Produces animation preview descriptors."""

    def render(self, board: dict[str, Any]) -> dict[str, Any]:
        return {
            "frame": board.get("frame", 1),
            "animation": board.get("animation", "fade-in"),
            "duration": board.get("duration", 2.5),
            "preview": None,
        }


_animation_preview: AnimationPreview | None = None


def get_animation_preview() -> AnimationPreview:
    global _animation_preview
    if _animation_preview is None:
        _animation_preview = AnimationPreview()
    return _animation_preview
