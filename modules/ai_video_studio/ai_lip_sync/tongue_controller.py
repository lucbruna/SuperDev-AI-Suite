"""Tongue Controller — tongue visibility driven by dental/alveolar phonemes."""
from __future__ import annotations

from typing import Any

# Phonemes that visibly involve the tongue tip.
_TONGUE_PHONEMES = {"T", "D", "N", "L", "S", "Z", "TH", "DH", "SH", "ZH"}


def tongue_curve(timeline: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Per-frame tongue visibility (0-1)."""
    out: list[dict[str, Any]] = []
    for f in timeline:
        phoneme = f.get("phoneme", "")
        visible = 1.0 if phoneme in _TONGUE_PHONEMES else 0.0
        out.append({"frame": f.get("frame"), "time": f.get("time"), "value": visible})
    return out
