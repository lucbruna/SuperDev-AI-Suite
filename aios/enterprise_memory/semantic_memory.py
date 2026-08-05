"""AIOS Semantic Memory — declarative facts.

Facts are triples (subject, relation, value) with tags. Recall by
subject, relation or tag.
"""

from __future__ import annotations

import time
import uuid
from typing import Any


class SemanticMemory:
    """Store of (subject, relation, value) facts."""

    def __init__(self, max_facts: int = 10_000) -> None:
        self._facts: list[dict[str, Any]] = []
        self._max = max_facts

    def store(self, content: Any, **meta: Any) -> dict[str, Any]:
        if isinstance(content, dict):
            subject = content.get("subject")
            relation = content.get("relation")
            value = content.get("value")
        else:
            subject = meta.get("subject")
            relation = meta.get("relation")
            value = content
        fact = {
            "record_id": f"sem-{uuid.uuid4().hex[:10]}",
            "subject": subject,
            "relation": relation,
            "value": value,
            "tags": list(meta.get("tags", [])),
            "confidence": float(meta.get("confidence", 1.0)),
            "timestamp": time.time(),
        }
        self._facts.append(fact)
        if len(self._facts) > self._max:
            self._facts = self._facts[-self._max:]
        return fact

    def recall(self, query: Any = None, limit: int = 5, **filters: Any) -> list[dict[str, Any]]:
        subject = filters.get("subject")
        relation = filters.get("relation")
        tags = set(filters.get("tags", []))
        matches = []
        for fact in self._facts:
            if subject is not None and fact["subject"] != subject:
                continue
            if relation is not None and fact["relation"] != relation:
                continue
            if tags and not tags.issubset(set(fact["tags"])):
                continue
            if query is not None and str(query).lower() not in str(fact["value"]).lower():
                continue
            matches.append(fact)
            if len(matches) >= limit:
                break
        return matches

    def forget(self, record_id: str) -> bool:
        before = len(self._facts)
        self._facts = [f for f in self._facts if f["record_id"] != record_id]
        return len(self._facts) < before

    def clear(self) -> None:
        self._facts.clear()

    def stats(self) -> dict[str, Any]:
        return {"facts": len(self._facts), "max": self._max}

    def snapshot(self) -> dict[str, Any]:
        return {"facts": len(self._facts), "max": self._max}
