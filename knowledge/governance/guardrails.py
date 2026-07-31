from __future__ import annotations

import logging
from typing import Any

from ..knowledge_models import KnowledgeItem


class Guardrails:
    """Applies content and access guardrails before storage."""

    def __init__(self, blocked_terms: list[str] | None = None, max_content_chars: int = 100000) -> None:
        self._log = logging.getLogger("superdev.knowledge.governance.guardrails")
        self.blocked_terms = [term.lower() for term in (blocked_terms or [])]
        self.max_content_chars = max(1, max_content_chars)

    def check(self, item: KnowledgeItem | str) -> tuple[bool, str]:
        content = item.content if isinstance(item, KnowledgeItem) else item
        lowered = content.lower()
        for term in self.blocked_terms:
            if term in lowered:
                return False, f"blocked term: {term}"
        if len(content) > self.max_content_chars:
            return False, f"content exceeds {self.max_content_chars} characters"
        return True, "ok"
