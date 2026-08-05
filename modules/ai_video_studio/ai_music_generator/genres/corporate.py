"""Corporate — clean, professional background music."""
from __future__ import annotations

GENRE = {
    "name": "Corporate",
    "bpm": 100,
    "root": "G",
    "scale": "major",
    "progression": [("0", "major"), ("4", "major"), ("5", "major"), ("0", "major")],
    "instruments": ["piano", "synthesizer", "bass"],
    "arpeggio": True,
    "swing": 0.0,
    "density": 0.5,
    "bass_pattern": "root_four",
    "drums_pattern": "none",
}


def get_genre() -> dict:
    return dict(GENRE)
