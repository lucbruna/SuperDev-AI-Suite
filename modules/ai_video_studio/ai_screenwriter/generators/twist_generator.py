"""Twist generator — creates unexpected turns in scripts."""
from __future__ import annotations


class TwistGenerator:
    """Generates a plot twist for narrative scripts."""

    def generate(self, topic: str) -> str:
        if not topic:
            return "No final, descobrimos que tudo era parte do plano."
        return f"Reviravolta: o que parecia simples sobre {topic.lower()} era apenas o começo."


_twist_generator: TwistGenerator | None = None


def get_twist_generator() -> TwistGenerator:
    global _twist_generator
    if _twist_generator is None:
        _twist_generator = TwistGenerator()
    return _twist_generator
