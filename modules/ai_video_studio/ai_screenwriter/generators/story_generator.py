"""Story generator — builds a narrative arc from a brief."""
from __future__ import annotations

from typing import Any


class StoryGenerator:
    """Generates a narrative arc with setup, conflict and resolution."""

    def generate(self, brief: str) -> dict[str, Any]:
        return {
            "setup": f"Introduzimos o contexto de {brief.lower() or 'nosso tema'}.",
            "conflict": "Aparece um desafio que precisa de atenção.",
            "resolution": "Com a abordagem certa, o problema se resolve.",
            "arc": ["setup", "conflict", "resolution"],
        }


_story_generator: StoryGenerator | None = None


def get_story_generator() -> StoryGenerator:
    global _story_generator
    if _story_generator is None:
        _story_generator = StoryGenerator()
    return _story_generator
