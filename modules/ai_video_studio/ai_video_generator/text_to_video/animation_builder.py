"""Animation builder — assemble character animations for a shot."""
from __future__ import annotations

from typing import Any


class AnimationBuilder:
    """Plans which animation clip to play for each character."""

    _CLIPS = ["idle", "walk", "run", "jump", "talk", "wave", "sit"]

    def build(self, characters: list[dict[str, Any]], action: str = "idle") -> dict[str, Any]:
        clip = action if action in self._CLIPS else "idle"
        return {
            "clip": clip,
            "characters": [
                {"name": ch.get("name", "unnamed"), "loop": clip != "talk"} for ch in characters
            ],
        }

    def available_clips(self) -> list[str]:
        return list(self._CLIPS)
