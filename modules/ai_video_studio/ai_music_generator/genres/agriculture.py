"""Agriculture — earthy, folk-inspired fields music."""
from __future__ import annotations

GENRE = {
    "name": "Agriculture",
    "bpm": 92,
    "root": "D",
    "scale": "mixolydian",
    "progression": [("0", "major"), ("5", "major"), ("3", "minor"), ("4", "major")],
    "instruments": ["guitar", "flute", "bass"],
    "arpeggio": True,
    "swing": 0.05,
    "density": 0.5,
    "bass_pattern": "root_four",
    "drums_pattern": "none",
}


def get_genre() -> dict:
    return dict(GENRE)
