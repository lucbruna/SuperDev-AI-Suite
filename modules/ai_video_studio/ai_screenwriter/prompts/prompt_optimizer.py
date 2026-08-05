"""Prompt optimizer — refines prompts for better generation results."""
from __future__ import annotations

from typing import Any


class PromptOptimizer:
    """Improves prompts by adding clarity and constraints."""

    def optimize(self, prompt: str, tone: str = "informative") -> dict[str, Any]:
        return {
            "prompt": prompt,
            "optimized": f"{prompt}\nRegras: seja claro, use {tone} e evite ambiguidade.",
            "tone": tone,
        }


_prompt_optimizer: PromptOptimizer | None = None


def get_prompt_optimizer() -> PromptOptimizer:
    global _prompt_optimizer
    if _prompt_optimizer is None:
        _prompt_optimizer = PromptOptimizer()
    return _prompt_optimizer
