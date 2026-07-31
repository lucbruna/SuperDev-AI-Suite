"""Semantic memory for concepts, facts, and knowledge graphs."""

from __future__ import annotations

import time
from typing import Any


class SemanticMemory:
    """Stores concepts, facts, and relationships between knowledge."""

    def __init__(self) -> None:
        self._concepts: dict[str, dict[str, Any]] = {}
        self._relations: dict[str, list[str]] = {}
        self._categories: dict[str, set[str]] = {}

    def store(self, key: str, value: Any, category: str = "general", metadata: dict[str, Any] | None = None) -> None:
        self._concepts[key] = {
            "value": value,
            "category": category,
            "metadata": metadata or {},
            "timestamp": time.time(),
            "confidence": metadata.get("confidence", 1.0) if metadata else 1.0,
        }
        self._categories.setdefault(category, set()).add(key)

    def retrieve(self, key: str) -> Any | None:
        concept = self._concepts.get(key)
        return concept.get("value") if concept else None

    def get_concept(self, key: str) -> dict[str, Any] | None:
        return self._concepts.get(key)

    def add_relation(self, subject: str, predicate: str, obj: str) -> None:
        rel_key = f"{subject}:{predicate}"
        self._relations.setdefault(rel_key, []).append(obj)

    def get_relations(self, subject: str, predicate: str | None = None) -> list[str]:
        results: list[str] = []
        for rel_key, targets in self._relations.items():
            sub, pred = rel_key.split(":", 1)
            if sub == subject and (predicate is None or pred == predicate):
                results.extend(targets)
        return results

    def get_by_category(self, category: str) -> dict[str, Any]:
        keys = self._categories.get(category, set())
        return {k: self._concepts[k] for k in keys if k in self._concepts}

    def categories(self) -> list[str]:
        return list(self._categories.keys())

    def remove(self, key: str) -> bool:
        removed = key in self._concepts
        if removed:
            cat = self._concepts[key].get("category", "general")
            self._concepts.pop(key)
            self._categories.get(cat, set()).discard(key)
            self._relations = {rk: [t for t in targets if t != key] for rk, targets in self._relations.items()}
        return removed

    def count(self) -> int:
        return len(self._concepts)

    def clear(self) -> None:
        self._concepts.clear()
        self._relations.clear()
        self._categories.clear()

    def snapshot(self) -> dict[str, Any]:
        return {
            "concepts": len(self._concepts),
            "relations": len(self._relations),
            "categories": list(self._categories.keys()),
        }
