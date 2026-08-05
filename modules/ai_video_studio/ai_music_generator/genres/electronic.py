"""Electronic — synthetic dance feel."""
from __future__ import annotations

GENRE = {
    "name": "Electronic",
    "bpm": 124,
    "root": "A",
    "scale": "natural_minor",
    "progression": [("0", "minor"), ("6", "major"), ("3", "minor"), ("5", "major")],
    "instruments": ["synthesizer", "bass", "drums"],
    "arpeggio": True,
    "swing": 0.0,
    "density": 0.9,
    "bass_pattern": "root_eighth",
    "drums_pattern": "four_on_floor",
}


def get_genre() -> dict:
    return dict(GENRE)
