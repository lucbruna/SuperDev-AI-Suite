"""Jazz — swing feel with 7th chords."""
from __future__ import annotations

GENRE = {
    "name": "Jazz",
    "bpm": 108,
    "root": "F",
    "scale": "major",
    "progression": [("0", "major7"), ("4", "major7"), ("1", "minor7"), ("5", "dom7")],
    "instruments": ["piano", "trumpet", "bass", "drums"],
    "arpeggio": True,
    "swing": 0.35,
    "density": 0.7,
    "bass_pattern": "root_eighth",
    "drums_pattern": "swing",
}


def get_genre() -> dict:
    return dict(GENRE)
