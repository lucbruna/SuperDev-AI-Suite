from __future__ import annotations

from typing import Any

from .concepts import Concept
from .entities import Entity
from .semantic_links import SemanticLink


class SemanticSearch:
    """Search over semantic knowledge."""

    def search(
        self,
        query: str,
        concepts: dict[str, Concept],
        entities: dict[str, Entity],
        links: list[SemanticLink],
    ) -> list[dict[str, Any]]:
        q = query.lower()
        results: list[dict[str, Any]] = []
        for name, concept in concepts.items():
            if q in name.lower() or q in concept.definition.lower():
                results.append({"type": "concept", "name": name, "data": concept.to_dict()})
        for eid, entity in entities.items():
            if q in entity.name.lower() or q in eid.lower():
                results.append({"type": "entity", "id": eid, "data": entity.to_dict()})
        for link in links:
            if q in link.link_type.lower():
                results.append({"type": "link", "data": link.to_dict()})
        return results
