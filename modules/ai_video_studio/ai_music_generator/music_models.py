"""Music models — notes, tracks and song structures for the music generator."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Note:
    """A single musical event."""

    name: str          # pitch name like "C4", or drum name like "kick"
    start: float       # beat time (0-based)
    duration: float    # in beats
    velocity: float = 0.8
    instrument: str = "piano"

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "start": self.start, "duration": self.duration,
                "velocity": self.velocity, "instrument": self.instrument}


@dataclass
class Track:
    """A monophonic instrument track."""

    instrument: str
    notes: list[Note] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"instrument": self.instrument, "notes": [n.to_dict() for n in self.notes]}


@dataclass
class Song:
    """A full composition: metadata + tracks."""

    title: str
    genre: str
    bpm: float
    key: str
    tracks: list[Track] = field(default_factory=list)
    bars: int = 4

    def to_dict(self) -> dict[str, Any]:
        return {"title": self.title, "genre": self.genre, "bpm": self.bpm,
                "key": self.key, "bars": self.bars,
                "tracks": [t.to_dict() for t in self.tracks]}
