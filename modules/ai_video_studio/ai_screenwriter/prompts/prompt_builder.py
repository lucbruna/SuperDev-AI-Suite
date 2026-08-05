"""Prompt builder — composes structured prompts for script generation."""
from __future__ import annotations

from typing import Any


class PromptBuilder:
    """Builds a structured prompt string from parts."""

    def build(self, brief: str, role: str = "roteirista", tone: str = "informative") -> dict[str, Any]:
        return {
            "role": role,
            "task": f"Escreva um roteiro sobre: {brief}",
            "constraints": f"Tom: {tone}. Linguagem natural e fluida.",
            "full": f"{role}: {brief}. Tom: {tone}.",
        }


_prompt_builder: PromptBuilder | None = None


def get_prompt_builder() -> PromptBuilder:
    global _prompt_builder
    if _prompt_builder is None:
        _prompt_builder = PromptBuilder()
    return _prompt_builder
