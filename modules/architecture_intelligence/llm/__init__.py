"""LLM layer: provider abstraction and prompt templates."""
from __future__ import annotations

from modules.architecture_intelligence.llm.provider import (
    LLMProvider,
    complete,
    get_provider,
)
from modules.architecture_intelligence.llm.prompts import (
    executive_prompt,
    qa_prompt,
)

__all__ = [
    "LLMProvider",
    "complete",
    "get_provider",
    "executive_prompt",
    "qa_prompt",
]
