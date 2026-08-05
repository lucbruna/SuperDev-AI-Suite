"""Meditation — calm, sparse and slow."""
from __future__ import annotations

GENRE = {
    "name": "Meditation",
    "bpm": 52,
    "root": "D",
    "scale": "major",
    "progression": [("0", "major"), ("5", "major"), ("3", "minor"), ("0", "major")],
    "instruments": ["flute", "choir", "synthesizer"],
    "arpeggio": False,
    "swing": 0.0,
    "density": 0.3,
    "bass_pattern": "root_four",
    "drums_pattern": "none",
}


def get_genre() -> dict:
    return dict(GENRE)
