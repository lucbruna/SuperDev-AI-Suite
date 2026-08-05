"""Suspense — tense, minimal and pulsing."""
from __future__ import annotations

GENRE = {
    "name": "Suspense",
    "bpm": 96,
    "root": "A",
    "scale": "harmonic_minor",
    "progression": [("0", "minor"), ("1", "dim"), ("5", "major"), ("6", "major")],
    "instruments": ["violin", "cello", "drums"],
    "arpeggio": False,
    "swing": 0.0,
    "density": 0.6,
    "bass_pattern": "root_four",
    "drums_pattern": "pulse",
}


def get_genre() -> dict:
    return dict(GENRE)
