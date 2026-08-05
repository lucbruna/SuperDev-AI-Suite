"""Prompt examples — example prompts for few-shot usage."""
from __future__ import annotations

from typing import Any

EXAMPLES = [
    {"input": "energia solar", "output": "Roteiro educativo sobre energia solar para iniciantes."},
    {"input": "marketing digital", "output": "Roteiro de vendas com gancho forte e CTA claro."},
]


class PromptExamples:
    """Provides few-shot example prompts."""

    def all(self) -> list[dict[str, Any]]:
        return EXAMPLES

    def sample(self, limit: int = 1) -> list[dict[str, Any]]:
        return EXAMPLES[:limit]


_prompt_examples: PromptExamples | None = None


def get_prompt_examples() -> PromptExamples:
    global _prompt_examples
    if _prompt_examples is None:
        _prompt_examples = PromptExamples()
    return _prompt_examples
