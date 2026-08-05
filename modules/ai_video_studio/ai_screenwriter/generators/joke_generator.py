"""Joke generator — creates light humor lines for scripts."""
from __future__ import annotations


class JokeGenerator:
    """Generates a light joke line."""

    def generate(self, topic: str) -> str:
        if not topic:
            return "Por que o vídeo foi bem? Porque ele não perdeu o ritmo!"
        return f"Falando em {topic.lower() or 'isso'}: é mais fácil do que parece — quase."


_joke_generator: JokeGenerator | None = None


def get_joke_generator() -> JokeGenerator:
    global _joke_generator
    if _joke_generator is None:
        _joke_generator = JokeGenerator()
    return _joke_generator
