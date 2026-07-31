from __future__ import annotations

import logging
from typing import Any

from ..knowledge_models import RetrievalContext


class ResponseGenerator:
    """Generates a local, template-based answer from the retrieval context."""

    def __init__(self, max_answer_chars: int = 800, require_context: bool = True) -> None:
        self._log = logging.getLogger("superdev.knowledge.rag.response_generator")
        self._max_answer_chars = max_answer_chars
        self._require_context = require_context

    def generate(self, query: str, context: RetrievalContext, prompt: dict[str, str] | None = None) -> dict[str, Any]:
        if not context.results:
            answer = "No relevant knowledge found to answer this question."
        elif self._require_context:
            answer = context.results[0].text
        else:
            answer = context.results[0].text
        if len(answer) > self._max_answer_chars:
            answer = answer[: self._max_answer_chars]
        used_sources = [result.source for result in context.results]
        score = context.results[0].score if context.results else 0.0
        return {"answer": answer, "used_sources": used_sources, "score": score}
