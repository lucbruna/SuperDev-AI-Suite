"""Horror — dissonant drones and eerie strings."""
from __future__ import annotations

GENRE = {
    "name": "Horror",
    "bpm": 60,
    "root": "B",
    "scale": "chromatic",
    "progression": [("0", "minor"), ("1", "dim"), ("0", "minor"), ("1", "dim")],
    "instruments": ["violin", "choir", "synthesizer"],
    "arpeggio": False,
    "swing": 0.0,
    "density": 0.4,
    "bass_pattern": "root_four",
    "drums_pattern": "none",
}


def get_genre() -> dict:
    return dict(GENRE)
