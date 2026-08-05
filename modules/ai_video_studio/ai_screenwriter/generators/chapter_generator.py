"""Chapter generator — splits a script into chapters."""
from __future__ import annotations

from typing import Any


class ChapterGenerator:
    """Splits text into chapter-like segments."""

    def generate(self, text: str, chapters: int = 3) -> list[dict[str, Any]]:
        words = text.split()
        if not words:
            return []
        size = max(1, len(words) // max(chapters, 1))
        return [
            {"chapter": i + 1, "text": " ".join(words[i * size:(i + 1) * size])}
            for i in range(min(chapters, max(1, len(words) // max(size, 1) + 1)))
        ]


_chapter_generator: ChapterGenerator | None = None


def get_chapter_generator() -> ChapterGenerator:
    global _chapter_generator
    if _chapter_generator is None:
        _chapter_generator = ChapterGenerator()
    return _chapter_generator
