"""Lo-fi — chill, downtempo and slightly detuned."""
from __future__ import annotations

GENRE = {
    "name": "Lo-fi",
    "bpm": 78,
    "root": "D",
    "scale": "dorian",
    "progression": [("0", "minor7"), ("5", "dom7"), ("3", "minor7"), ("4", "major7")],
    "instruments": ["piano", "synthesizer", "drums"],
    "arpeggio": False,
    "swing": 0.12,
    "density": 0.5,
    "bass_pattern": "root_four",
    "drums_pattern": "backbeat",
}


def get_genre() -> dict:
    return dict(GENRE)
