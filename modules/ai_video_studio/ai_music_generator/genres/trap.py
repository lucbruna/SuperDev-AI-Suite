"""Trap — 808 bass and halftime drums."""
from __future__ import annotations

GENRE = {
    "name": "Trap",
    "bpm": 140,
    "root": "C#",
    "scale": "natural_minor",
    "progression": [("0", "minor"), ("6", "major"), ("3", "minor"), ("5", "major")],
    "instruments": ["synthesizer", "bass", "drums"],
    "arpeggio": False,
    "swing": 0.1,
    "density": 0.8,
    "bass_pattern": "root_eighth",
    "drums_pattern": "trap",
}


def get_genre() -> dict:
    return dict(GENRE)
