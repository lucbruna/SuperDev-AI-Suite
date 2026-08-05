"""Narration generator — creates voiceover narration lines."""
from __future__ import annotations


class NarrationGenerator:
    """Generates narration for the video."""

    def generate(self, brief: str) -> str:
        if not brief:
            return "Nesta apresentação, vamos descobrir algo novo."
        return f"O tema de hoje é {brief.lower()}. Vamos entender como isso funciona na prática."


_narration_generator: NarrationGenerator | None = None


def get_narration_generator() -> NarrationGenerator:
    global _narration_generator
    if _narration_generator is None:
        _narration_generator = NarrationGenerator()
    return _narration_generator
