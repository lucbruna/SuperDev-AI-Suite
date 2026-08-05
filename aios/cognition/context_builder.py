"""AIOS Context Builder — enrich inputs into a working context.

Combines raw input, selected percepts and detected intent into a
structured context used by planners and agents.
"""

from __future__ import annotations

import time
from typing import Any


class ContextBuilder:
    """Assemble a rich execution context."""

    def build(
        self,
        raw_input: Any,
        percepts: list[dict[str, Any]] | None = None,
        intent: dict[str, Any] | None = None,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return {
            "input": raw_input,
            "percepts": percepts or [],
            "intent": intent or {"intent": "unknown", "confidence": 0.0},
            "extra": extra or {},
            "built_at": time.time(),
        }

    def merge(self, *contexts: dict[str, Any]) -> dict[str, Any]:
        """Merge multiple contexts; later contexts win on conflicts."""
        merged: dict[str, Any] = {}
        for context in contexts:
            merged.update(context)
        return merged
