from __future__ import annotations

import logging

from ..knowledge_models import RetrievalContext

DEFAULT_SYSTEM_PROMPT = (
    "You are a precise assistant. Answer the user's question using only the "
    "provided context. If the context does not contain the answer, say so "
    "instead of inventing information."
)


class PromptBuilder:
    """Builds a system/user prompt pair from a query and retrieval context."""

    def __init__(self, system_prompt: str = DEFAULT_SYSTEM_PROMPT, max_context_chars: int = 4000) -> None:
        self._log = logging.getLogger("superdev.knowledge.rag.prompt_builder")
        self._system_prompt = system_prompt
        self._max_context_chars = max_context_chars

    def build(self, query: str, context: RetrievalContext) -> dict[str, str]:
        context_text = context.context_text()
        if len(context_text) > self._max_context_chars:
            context_text = context_text[: self._max_context_chars]
        return {
            "system": self._system_prompt,
            "user": f"Context:\n{context_text}\n\nQuestion: {query}\n\nAnswer:",
        }
