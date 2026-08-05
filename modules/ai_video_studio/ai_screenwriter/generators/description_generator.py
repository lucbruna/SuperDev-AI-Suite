"""Description generator — creates scene or visual descriptions."""
from __future__ import annotations


class DescriptionGenerator:
    """Generates descriptive text for scenes."""

    def generate(self, scene: str) -> str:
        if not scene:
            return "Cena genérica com ambiente claro e profissional."
        return f"Cena: {scene}. Ambiente bem iluminado, enquadramento central."


_description_generator: DescriptionGenerator | None = None


def get_description_generator() -> DescriptionGenerator:
    global _description_generator
    if _description_generator is None:
        _description_generator = DescriptionGenerator()
    return _description_generator
