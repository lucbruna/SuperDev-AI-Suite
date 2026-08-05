"""Pop — catchy major-key song feel."""
from __future__ import annotations

GENRE = {
    "name": "Pop",
    "bpm": 112,
    "root": "C",
    "scale": "major",
    "progression": [("0", "major"), ("5", "major"), ("3", "minor"), ("4", "major")],
    "instruments": ["piano", "synthesizer", "bass", "drums"],
    "arpeggio": True,
    "swing": 0.02,
    "density": 0.8,
    "bass_pattern": "root_four",
    "drums_pattern": "four_on_floor",
}


def get_genre() -> dict:
    return dict(GENRE)
