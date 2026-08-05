"""TikTok Music — music browsing and selection for posts (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class TikTokMusic:
    """Curate and rank music tracks for TikTok posts."""

    def __init__(self) -> None:
        self._library: list[dict] = [
            {"id": "m001", "title": "Lo-Fi Focus", "genre": "lofi", "energy": 0.3, "duration": 30},
            {"id": "m002", "title": "Synth Pop Uplift", "genre": "pop", "energy": 0.8, "duration": 45},
            {"id": "m003", "title": "Deep Bass Hype", "genre": "hiphop", "energy": 0.9, "duration": 60},
            {"id": "m004", "title": "Ambient Chill", "genre": "ambient", "energy": 0.2, "duration": 30},
            {"id": "m005", "title": "Tropical Vibes", "genre": "pop", "energy": 0.6, "duration": 60},
        ]

    def search(self, *, query: str = "", genre: str = "", min_energy: float = 0.0) -> dict:
        """Search the music library with filtering."""
        results = []
        for track in self._library:
            if query and query.lower() not in track["title"].lower():
                continue
            if genre and track["genre"] != genre.lower():
                continue
            if track["energy"] < min_energy:
                continue
            results.append(track)
        return {"results": results, "count": len(results)}

    def recommend(self, *, duration_seconds: float = 30.0, mood: str = "energetic") -> dict:
        """Pick a track matching duration and mood energy."""
        target = 0.8 if mood in ("energetic", "hype", "upbeat") else 0.3
        ranked = sorted(self._library, key=lambda t: abs(t["energy"] - target) + abs(t["duration"] - duration_seconds) / 100.0)
        return {"recommended": ranked[0] if ranked else None}

    def stats(self) -> dict[str, int]:
        return {"library_size": len(self._library)}


_MUSIC: TikTokMusic | None = None


def get_tiktok_music() -> TikTokMusic:
    """Get the module-level singleton music library."""
    global _MUSIC
    if _MUSIC is None:
        _MUSIC = TikTokMusic()
    return _MUSIC
