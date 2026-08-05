"""Title generator — creates catchy video titles."""
from __future__ import annotations


class TitleGenerator:
    """Generates a video title from a topic."""

    def generate(self, topic: str) -> str:
        if not topic:
            return "Vídeo"
        return f"{topic.title()} — O Guia Definitivo"


_title_generator: TitleGenerator | None = None


def get_title_generator() -> TitleGenerator:
    global _title_generator
    if _title_generator is None:
        _title_generator = TitleGenerator()
    return _title_generator
