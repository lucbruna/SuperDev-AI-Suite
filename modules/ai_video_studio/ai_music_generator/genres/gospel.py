"""Gospel — uplifting organ/choir feel."""
from __future__ import annotations

GENRE = {
    "name": "Gospel",
    "bpm": 84,
    "root": "F",
    "scale": "major",
    "progression": [("0", "major"), ("4", "major"), ("1", "minor"), ("5", "major")],
    "instruments": ["piano", "choir", "organ", "drums"],
    "arpeggio": False,
    "swing": 0.0,
    "density": 0.8,
    "bass_pattern": "root_four",
    "drums_pattern": "four_on_floor",
}


def get_genre() -> dict:
    return dict(GENRE)
