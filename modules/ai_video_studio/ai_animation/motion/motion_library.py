"""Motion library — central registry of motion clips."""
from __future__ import annotations

from typing import Any

_CLIPS = {
    "walk": {"frames": 24, "loops": True, "blend_time": 0.2},
    "run": {"frames": 18, "loops": True, "blend_time": 0.15},
    "jump": {"frames": 30, "loops": False, "blend_time": 0.25},
    "idle": {"frames": 60, "loops": True, "blend_time": 0.4},
    "wave": {"frames": 48, "loops": False, "blend_time": 0.3},
    "sit": {"frames": 40, "loops": True, "blend_time": 0.5},
}


class MotionLibrary:
    """Stores and fetches motion clip definitions."""

    def __init__(self) -> None:
        self._clips = {name: dict(clip) for name, clip in _CLIPS.items()}

    def register(self, name: str, clip: dict[str, Any]) -> None:
        self._clips[name] = clip

    def fetch(self, action: str) -> dict[str, Any] | None:
        clip = self._clips.get(action)
        return dict(clip) if clip else None

    def available(self) -> list[str]:
        return list(self._clips.keys())


_motion_library: MotionLibrary | None = None


def get_motion_library() -> MotionLibrary:
    global _motion_library
    if _motion_library is None:
        _motion_library = MotionLibrary()
    return _motion_library
