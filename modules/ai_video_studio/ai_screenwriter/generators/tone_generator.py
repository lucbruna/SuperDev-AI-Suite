"""Tone generator — applies a tone to script text."""
from __future__ import annotations

from typing import Any

TONE_PREFIX = {
    "informative": "Vamos entender: ",
    "fun": "Bora descobrir: ",
    "serious": "É importante saber: ",
    "inspirational": "Acredite: ",
    "educational": "Aprenda: ",
}


class ToneGenerator:
    """Adjusts script tone via prefixes and tone metadata."""

    def apply(self, text: str, tone: str = "informative") -> dict[str, Any]:
        prefix = TONE_PREFIX.get(tone, "")
        return {"text": f"{prefix}{text}" if prefix else text, "tone": tone}


_tone_generator: ToneGenerator | None = None


def get_tone_generator() -> ToneGenerator:
    global _tone_generator
    if _tone_generator is None:
        _tone_generator = ToneGenerator()
    return _tone_generator
