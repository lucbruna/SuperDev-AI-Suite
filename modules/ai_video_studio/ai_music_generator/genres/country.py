"""Country — rootsy acoustic feel."""
from __future__ import annotations

GENRE = {
    "name": "Country",
    "bpm": 104,
    "root": "G",
    "scale": "major",
    "progression": [("0", "major"), ("4", "major"), ("5", "major"), ("0", "major")],
    "instruments": ["guitar", "fiddle", "bass", "drums"],
    "arpeggio": True,
    "swing": 0.05,
    "density": 0.6,
    "bass_pattern": "root_four",
    "drums_pattern": "backbeat",
}


def get_genre() -> dict:
    return dict(GENRE)
