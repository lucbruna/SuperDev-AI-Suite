"""Hip-hop — groovy boom-bap feel."""
from __future__ import annotations

GENRE = {
    "name": "Hip-hop",
    "bpm": 92,
    "root": "F",
    "scale": "natural_minor",
    "progression": [("0", "minor"), ("5", "major"), ("3", "minor"), ("6", "major")],
    "instruments": ["synthesizer", "bass", "drums"],
    "arpeggio": False,
    "swing": 0.15,
    "density": 0.7,
    "bass_pattern": "root_eighth",
    "drums_pattern": "backbeat",
}


def get_genre() -> dict:
    return dict(GENRE)
