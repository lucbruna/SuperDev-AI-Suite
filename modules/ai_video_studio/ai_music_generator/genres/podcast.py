"""Podcast — unobtrusive intro/outro music bed."""
from __future__ import annotations

GENRE = {
    "name": "Podcast",
    "bpm": 88,
    "root": "C",
    "scale": "major",
    "progression": [("0", "major"), ("3", "minor"), ("4", "major"), ("5", "major")],
    "instruments": ["piano", "synthesizer", "drums"],
    "arpeggio": True,
    "swing": 0.0,
    "density": 0.5,
    "bass_pattern": "root_four",
    "drums_pattern": "backbeat",
}


def get_genre() -> dict:
    return dict(GENRE)
