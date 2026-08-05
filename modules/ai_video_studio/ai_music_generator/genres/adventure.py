"""Adventure — heroic quest feel."""
from __future__ import annotations

GENRE = {
    "name": "Adventure",
    "bpm": 120,
    "root": "D",
    "scale": "major",
    "progression": [("0", "major"), ("5", "major"), ("3", "minor"), ("4", "major")],
    "instruments": ["piano", "violin", "trumpet", "drums"],
    "arpeggio": True,
    "swing": 0.0,
    "density": 0.8,
    "bass_pattern": "root_eighth",
    "drums_pattern": "four_on_floor",
}


def get_genre() -> dict:
    return dict(GENRE)
