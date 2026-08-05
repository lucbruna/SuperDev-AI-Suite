"""Music Optimizer — reduces render cost without changing the sound much."""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class MusicOptimizer:
    """Applies safe optimisations to a song before rendering."""

    def __init__(self, max_polyphony: int = 6) -> None:
        self.max_polyphony = max_polyphony

    def dedupe(self, notes: list[Any]) -> list[Any]:
        """Drop exact duplicate note events (same pitch, same start).

        Accepts ``Note`` objects or plain dicts.
        """
        seen: set[tuple] = set()
        out: list[Any] = []
        for note in notes:
            name = note.name if not isinstance(note, dict) else note["name"]
            start = note.start if not isinstance(note, dict) else note["start"]
            instrument = note.instrument if not isinstance(note, dict) else note["instrument"]
            key = (name, round(start, 3), instrument)
            if key in seen:
                continue
            seen.add(key)
            out.append(note)
        return out

    def cache_key(self, instrument: str, name: str, velocity: float) -> str:
        return f"{instrument}:{name}:{round(velocity, 2)}"

    def stats(self, song: dict[str, Any]) -> dict[str, Any]:
        total = sum(len(t["notes"]) for t in song.get("tracks", []))
        return {"notes": total, "tracks": len(song.get("tracks", [])),
                "max_polyphony": self.max_polyphony}
