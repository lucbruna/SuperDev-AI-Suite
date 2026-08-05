"""Rock — driving guitars and backbeat drums."""
from __future__ import annotations

GENRE = {
    "name": "Rock",
    "bpm": 132,
    "root": "E",
    "scale": "natural_minor",
    "progression": [("0", "minor"), ("6", "major"), ("3", "minor"), ("5", "major")],
    "instruments": ["guitar", "bass", "drums"],
    "arpeggio": False,
    "swing": 0.0,
    "density": 0.9,
    "bass_pattern": "root_eighth",
    "drums_pattern": "backbeat",
}


def get_genre() -> dict:
    return dict(GENRE)
