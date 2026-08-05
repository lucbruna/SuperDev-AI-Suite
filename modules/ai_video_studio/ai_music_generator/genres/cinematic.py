"""Cinematic — epic film-score feel."""
from __future__ import annotations

GENRE = {
    "name": "Cinematic",
    "bpm": 88,
    "root": "D",
    "scale": "natural_minor",
    "progression": [("0", "minor"), ("5", "major"), ("3", "major"), ("6", "major")],
    "instruments": ["piano", "choir", "violin", "drums"],
    "arpeggio": False,
    "swing": 0.0,
    "density": 0.7,
    "bass_pattern": "root_four",
    "drums_pattern": "four_on_floor",
}


def get_genre() -> dict:
    return dict(GENRE)
