"""Semantic memory for concepts, facts, and knowledge graphs."""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Set


class SemanticMemory:
    """Stores concepts, facts, and relationships between knowledge."""

    def __init__(self) -> None:
        self._concepts: Dict[str, Dict[str, Any]] = {}
        self._relations: Dict[str, List[str]] = {}
        self._categories: Dict[str, Set[str]] = {}

    def store(self, key: str, value: Any, category: str = "general",
              metadata: Optional[Dict[str, Any]] = None) -> None:
        self._concepts[key] = {
            "value": value,
            "category": category,
            "metadata": metadata or {},
            "timestamp": time.time(),
            "confidence": metadata.get("confidence", 1.0) if metadata else 1.0,
        }
        self._categories.setdefault(category, set()).add(key)

    def retrieve(self, key: str) -> Optional[Any]:
        concept = self._concepts.get(key)
        return concept.get("value") if concept else None

    def get_concept(self, key: str) -> Optional[Dict[str, Any]]:
        return self._concepts.get(key)

    def add_relation(self, subject: str, predicate: str, obj: str) -> None:
        rel_key = f"{subject}:{predicate}"
        self._relations.setdefault(rel_key, []).append(obj)

    def get_relations(self, subject: str, predicate: Optional[str] = None) -> List[str]:
        results: List[str] = []
        for rel_key, targets in self._relations.items():
            sub, pred = rel_key.split(":", 1)
            if sub == subject and (predicate is None or pred == predicate):
                results.extend(targets)
        return results

    def get_by_category(self, category: str) -> Dict[str, Any]:
        keys = self._categories.get(category, set())
        return {k: self._concepts[k] for k in keys if k in self._concepts}

    def categories(self) -> List[str]:
        return list(self._categories.keys())

    def remove(self, key: str) -> bool:
        removed = key in self._concepts
        if removed:
            cat = self._concepts[key].get("category", "general")
            self._concepts.pop(key)
            self._categories.get(cat, set()).discard(key)
            self._relations = {
                rk: [t for t in targets if t != key]
                for rk, targets in self._relations.items()
            }
        return removed

    def count(self) -> int:
        return len(self._concepts)

    def clear(self) -> None:
        self._concepts.clear()
        self._relations.clear()
        self._categories.clear()

    def snapshot(self) -> Dict[str, Any]:
        return {
            "concepts": len(self._concepts),
            "relations": len(self._relations),
            "categories": list(self._categories.keys()),
        }
