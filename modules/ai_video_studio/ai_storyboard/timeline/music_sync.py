"""Music sync — maps music cues to storyboard beats."""
from __future__ import annotations

from typing import Any


class MusicSync:
    """Assigns music cues to boards based on scene mood."""

    MOOD_MUSIC = {
        "intro": "uplifting",
        "opening": "ambient",
        "presentation": "corporate",
        "explanation": "educational",
        "comparison": "dramatic",
        "product": "energetic",
        "testimonial": "emotional",
        "closing": "inspiring",
        "credits": "soft",
        "outro": "uplifting",
    }

    def assign(self, boards: list[dict[str, Any]]) -> list[dict[str, Any]]:
        for board in boards:
            board["music"] = self.MOOD_MUSIC.get(board.get("type", "presentation"), "neutral")
        return boards


_music_sync: MusicSync | None = None


def get_music_sync() -> MusicSync:
    global _music_sync
    if _music_sync is None:
        _music_sync = MusicSync()
    return _music_sync
