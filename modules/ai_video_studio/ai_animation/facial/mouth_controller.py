"""Mouth controller — mouth shapes for speech and expression."""
from __future__ import annotations

from typing import Any

_SHAPES = ("closed", "open", "smile", "frown", "round", "grin")


class MouthController:
    """Selects mouth shapes for phonemes and emotions."""

    def shape(self, phoneme: str = "") -> dict[str, Any]:
        normalized = phoneme.lower()
        if normalized in {"a", "ai", "ay"}:
            name = "open"
        elif normalized in {"e", "ee", "i"}:
            name = "grin"
        elif normalized in {"o", "oh", "ow"}:
            name = "round"
        elif normalized in {"m", "b", "p"}:
            name = "closed"
        else:
            name = "closed"
        return {"shape": name, "open_amount": 0.9 if name == "open" else 0.2}

    def available_shapes(self) -> list[str]:
        return list(_SHAPES)
