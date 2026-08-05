"""Music library — music track assets with mood metadata."""
from __future__ import annotations

from typing import Any


class MusicLibrary:
    """Catalogues music tracks by mood and tempo."""

    def __init__(self) -> None:
        self._tracks: dict[str, dict[str, Any]] = {}

    def register(self, name: str, *, ref: str, mood: str = "neutral", bpm: int = 120, duration_seconds: float = 60.0) -> None:
        if bpm <= 0:
            raise ValueError("bpm must be positive")
        self._tracks[name] = {
            "name": name,
            "ref": ref,
            "mood": mood,
            "bpm": bpm,
            "duration_seconds": duration_seconds,
        }

    def get(self, name: str) -> dict[str, Any] | None:
        return dict(self._tracks[name]) if name in self._tracks else None

    def by_mood(self, mood: str) -> list[str]:
        return [name for name, t in self._tracks.items() if t["mood"] == mood]

    def names(self) -> list[str]:
        return list(self._tracks.keys())
