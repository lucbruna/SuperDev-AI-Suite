"""Viseme Mapper — phoneme → viseme shape + mouth parameters.

A viseme is a visually distinct mouth shape. We use a compact set of 8
shapes (closed, open, wide, round, teeth, kiss, smile, neutral) plus
continuous parameters (open/round/wide/tense in 0-1) for animators.
"""
from __future__ import annotations

from typing import Any

# ARPABET-ish → (viseme, open, round, wide, tense)
_PHONEME_VISEMES: dict[str, tuple[str, float, float, float, float]] = {
    "AA": ("open", 0.9, 0.2, 0.4, 0.5),
    "AH": ("open", 0.6, 0.2, 0.3, 0.3),
    "AO": ("round", 0.7, 0.8, 0.2, 0.6),
    "AY": ("open", 0.8, 0.3, 0.5, 0.5),
    "EH": ("wide", 0.5, 0.1, 0.7, 0.6),
    "EY": ("wide", 0.6, 0.1, 0.8, 0.6),
    "IH": ("neutral", 0.3, 0.1, 0.5, 0.4),
    "IY": ("smile", 0.3, 0.1, 0.9, 0.8),
    "OW": ("round", 0.6, 0.7, 0.2, 0.5),
    "UW": ("kiss", 0.2, 1.0, 0.1, 0.9),
    "AW": ("round", 0.7, 0.6, 0.3, 0.5),
    "OY": ("round", 0.7, 0.6, 0.3, 0.5),
    "B": ("closed", 0.1, 0.0, 0.1, 0.8),
    "P": ("closed", 0.1, 0.0, 0.1, 0.8),
    "M": ("closed", 0.1, 0.0, 0.2, 0.6),
    "F": ("teeth", 0.3, 0.1, 0.6, 0.9),
    "V": ("teeth", 0.3, 0.1, 0.6, 0.9),
    "TH": ("teeth", 0.4, 0.2, 0.5, 0.9),
    "DH": ("teeth", 0.4, 0.2, 0.5, 0.9),
    "S": ("teeth", 0.2, 0.1, 0.8, 1.0),
    "Z": ("teeth", 0.2, 0.1, 0.8, 1.0),
    "SH": ("kiss", 0.3, 0.8, 0.2, 0.9),
    "ZH": ("kiss", 0.3, 0.8, 0.2, 0.9),
    "CH": ("kiss", 0.4, 0.8, 0.3, 0.9),
    "JH": ("kiss", 0.4, 0.8, 0.3, 0.9),
    "K": ("open", 0.5, 0.3, 0.4, 0.7),
    "G": ("open", 0.5, 0.3, 0.4, 0.7),
    "T": ("neutral", 0.3, 0.2, 0.4, 0.9),
    "D": ("neutral", 0.3, 0.2, 0.4, 0.9),
    "N": ("neutral", 0.3, 0.2, 0.4, 0.7),
    "L": ("wide", 0.4, 0.1, 0.6, 0.8),
    "R": ("round", 0.3, 0.5, 0.3, 0.7),
    "W": ("kiss", 0.3, 0.9, 0.1, 0.9),
    "Y": ("smile", 0.3, 0.2, 0.8, 0.8),
    "H": ("neutral", 0.4, 0.2, 0.4, 0.5),
    "NG": ("open", 0.5, 0.2, 0.3, 0.6),
    "PAUSE": ("closed", 0.0, 0.0, 0.0, 0.0),
}

VISEMES = sorted({v[0] for v in _PHONEME_VISEMES.values()})


def map_phoneme(phoneme: str) -> dict[str, Any]:
    """Return viseme + mouth params for a phoneme."""
    shape, open_, round_, wide, tense = _PHONEME_VISEMES.get(
        phoneme, ("neutral", 0.3, 0.1, 0.4, 0.4)
    )
    return {
        "phoneme": phoneme,
        "viseme": shape,
        "open": open_, "round": round_, "wide": wide, "tense": tense,
    }


def to_viseme_timeline(phoneme_timeline: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert a phoneme timeline to viseme entries (viseme persists)."""
    out: list[dict[str, Any]] = []
    last_viseme = "closed"
    for entry in phoneme_timeline:
        mapped = map_phoneme(entry["phoneme"])
        if mapped["viseme"] != last_viseme:
            out.append({**entry, **mapped})
            last_viseme = mapped["viseme"]
    return out
