"""Dialogue generator — creates natural spoken dialogue lines."""
from __future__ import annotations


class DialogueGenerator:
    """Generates dialogue lines for conversational segments."""

    def generate(self, topic: str, speaker: str = "Narrador") -> str:
        return f"{speaker}: vamos explorar {topic.lower() or 'este assunto'} de um jeito simples."


_dialogue_generator: DialogueGenerator | None = None


def get_dialogue_generator() -> DialogueGenerator:
    global _dialogue_generator
    if _dialogue_generator is None:
        _dialogue_generator = DialogueGenerator()
    return _dialogue_generator
