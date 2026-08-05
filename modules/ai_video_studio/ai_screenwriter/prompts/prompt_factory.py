"""Prompt factory — creates prompts by format and purpose."""
from __future__ import annotations

from typing import Any


class PromptFactory:
    """Produces prompt templates for common script formats."""

    PURPOSES = ["script", "hook", "title", "outline", "review"]

    def create(self, purpose: str, brief: str) -> dict[str, Any]:
        purpose = purpose if purpose in self.PURPOSES else "script"
        return {"purpose": purpose, "brief": brief, "template": f"template_{purpose}"}


_prompt_factory: PromptFactory | None = None


def get_prompt_factory() -> PromptFactory:
    global _prompt_factory
    if _prompt_factory is None:
        _prompt_factory = PromptFactory()
    return _prompt_factory
