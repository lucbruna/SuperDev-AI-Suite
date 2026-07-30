from __future__ import annotations

from typing import Any, Dict, List, Set


class ConceptMerger:
    """Merges related concepts into unified representations."""

    def __init__(self):
        self._merges: int = 0

    @property
    def merge_count(self) -> int:
        return self._merges

    def merge_concepts(self, concepts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not concepts:
            return []
        name_groups: Dict[str, List[Dict[str, Any]]] = {}
        for c in concepts:
            name = c.get("name", c.get("id", "unknown"))
            name_groups.setdefault(name, []).append(c)
        result: List[Dict[str, Any]] = []
        for name, group in name_groups.items():
            merged: Dict[str, Any] = {
                "name": name,
                "instance_count": len(group),
                "attributes": self._merge_attributes(group),
                "relationships": self._merge_relationships(group),
            }
            result.append(merged)
            self._merges += len(group) - 1
        return result

    def _merge_attributes(self, concepts: List[Dict[str, Any]]) -> Dict[str, Any]:
        merged: Dict[str, Any] = {}
        for c in concepts:
            attrs = c.get("attributes", {})
            if isinstance(attrs, dict):
                merged.update(attrs)
        return merged

    def _merge_relationships(self, concepts: List[Dict[str, Any]]) -> List[str]:
        rels: Set[str] = set()
        for c in concepts:
            r = c.get("relationships", [])
            if isinstance(r, list):
                rels.update(str(x) for x in r)
        return list(rels)

    def link_concepts(self, concept_a: Dict[str, Any], concept_b: Dict[str, Any]) -> Dict[str, Any]:
        self._merges += 1
        return {
            "name": f"{concept_a.get('name', '?')}_{concept_b.get('name', '?')}",
            "linked": True,
            "source_a": concept_a.get("name", "?"),
            "source_b": concept_b.get("name", "?"),
            "combined_attributes": {
                **concept_a.get("attributes", {}),
                **concept_b.get("attributes", {}),
            },
        }

    def reset(self) -> None:
        self._merges = 0
