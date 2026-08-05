"""Blues — classic 12-bar style, dominant 7ths."""
from __future__ import annotations

GENRE = {
    "name": "Blues",
    "bpm": 96,
    "root": "E",
    "scale": "minor_pentatonic",
    "progression": [("0", "dom7"), ("0", "dom7"), ("0", "dom7"), ("0", "dom7"),
                    ("3", "dom7"), ("3", "dom7"), ("0", "dom7"), ("0", "dom7"),
                    ("5", "dom7"), ("4", "dom7"), ("0", "dom7"), ("5", "dom7")],
    "instruments": ["guitar", "piano", "bass", "drums"],
    "arpeggio": False,
    "swing": 0.25,
    "density": 0.7,
    "bass_pattern": "root_four",
    "drums_pattern": "shuffle",
}


def get_genre() -> dict:
    return dict(GENRE)
