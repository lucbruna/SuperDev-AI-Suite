"""Quote generator — creates memorable quote lines."""
from __future__ import annotations


class QuoteGenerator:
    """Generates a memorable closing quote."""

    def generate(self, topic: str) -> str:
        if not topic:
            return "Grandes vídeos nascem de grandes mensagens."
        return f"No final, {topic.lower() or 'o essencial'} vale mais do que parece."


_quote_generator: QuoteGenerator | None = None


def get_quote_generator() -> QuoteGenerator:
    global _quote_generator
    if _quote_generator is None:
        _quote_generator = QuoteGenerator()
    return _quote_generator
