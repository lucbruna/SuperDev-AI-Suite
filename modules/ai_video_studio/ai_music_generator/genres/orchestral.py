"""Orchestral — classical string ensemble feel."""
from __future__ import annotations

GENRE = {
    "name": "Orchestral",
    "bpm": 76,
    "root": "C",
    "scale": "major",
    "progression": [("0", "major"), ("4", "major"), ("5", "major"), ("3", "minor")],
    "instruments": ["violin", "cello", "flute", "choir"],
    "arpeggio": True,
    "swing": 0.0,
    "density": 0.8,
    "bass_pattern": "root_four",
    "drums_pattern": "none",
}


def get_genre() -> dict:
    return dict(GENRE)
