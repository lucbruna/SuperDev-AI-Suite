"""AIOS Attention — relevance selection.

Scores items against focus terms/keywords and returns the top-N most
relevant, simulating attention over a candidate set.
"""

from __future__ import annotations

import re
from typing import Any

_WORD_RE = re.compile(r"[a-zA-Z0-9_]+")


class Attention:
    """Select the most relevant items from a candidate set."""

    def _tokens(self, text: Any) -> set[str]:
        return {t.lower() for t in _WORD_RE.findall(str(text))}

    def _score(self, item: Any, focus_tokens: set[str]) -> int:
        if not focus_tokens:
            return 1
        text = item
        if isinstance(item, dict):
            text = " ".join(str(v) for v in item.values())
        return len(focus_tokens & self._tokens(text))

    def filter(self, items: list[Any], focus: list[str] | None = None, limit: int = 5) -> list[dict[str, Any]]:
        """Return scored items sorted by relevance."""
        focus_tokens: set[str] = set()
        for term in focus or []:
            focus_tokens |= self._tokens(term)
        scored = [(self._score(item, focus_tokens), item) for item in items]
        scored.sort(key=lambda pair: -pair[0])
        return [
            {"score": score, "item": item}
            for score, item in scored[:limit]
            if score > 0 or not focus_tokens
        ]

    def focus_map(self, raw: dict[str, Any], keys: list[str]) -> dict[str, Any]:
        """Keep only the focused keys of a mapping."""
        return {key: raw[key] for key in keys if key in raw}
