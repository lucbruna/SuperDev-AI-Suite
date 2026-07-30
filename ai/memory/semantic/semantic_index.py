from __future__ import annotations

from typing import Any, Dict, List, Set

from .concepts import Concept
from .entities import Entity


class SemanticIndex:
    """Index structures for efficient semantic retrieval."""

    def __init__(self):
        self._concept_names: Set[str] = set()
        self._entity_ids: Set[str] = set()
        self._keyword_index: Dict[str, Set[str]] = {}

    @property
    def count(self) -> int:
        return len(self._concept_names) + len(self._entity_ids)

    def index_concept(self, concept: Concept) -> None:
        self._concept_names.add(concept.name)
        for word in concept.name.lower().split():
            self._keyword_index.setdefault(word, set()).add(concept.name)
        for word in concept.definition.lower().split():
            if len(word) > 3:
                self._keyword_index.setdefault(word, set()).add(concept.name)

    def index_entity(self, entity: Entity) -> None:
        self._entity_ids.add(entity.entity_id)
        for word in entity.name.lower().split():
            self._keyword_index.setdefault(word, set()).add(entity.entity_id)

    def search(self, query: str) -> List[str]:
        q = query.lower()
        results: Set[str] = set()
        for keyword, ids in self._keyword_index.items():
            if q in keyword or keyword in q:
                results.update(ids)
        return list(results)

    def clear(self) -> None:
        self._concept_names.clear()
        self._entity_ids.clear()
        self._keyword_index.clear()
