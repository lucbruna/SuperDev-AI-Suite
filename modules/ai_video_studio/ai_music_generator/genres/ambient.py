"""Ambient — slow pads, no drums."""
from __future__ import annotations

GENRE = {
    "name": "Ambient",
    "bpm": 60,
    "root": "C",
    "scale": "major",
    "progression": [("0", "major"), ("3", "minor"), ("4", "major"), ("2", "minor")],
    "instruments": ["choir", "synthesizer", "flute"],
    "arpeggio": False,
    "swing": 0.0,
    "density": 0.4,
    "bass_pattern": "root_four",
    "drums_pattern": "none",
}


def get_genre() -> dict:
    return dict(GENRE)
