from __future__ import annotations

from typing import Any

from .graph import KnowledgeGraph


class SemanticNetwork:
    """Semantic network built on a knowledge graph with typed relationships."""

    def __init__(self, graph: KnowledgeGraph | None = None):
        self._graph = graph or KnowledgeGraph()

    @property
    def graph(self) -> KnowledgeGraph:
        return self._graph

    def add_concept(self, concept_id: str, attributes: dict[str, Any] | None = None) -> None:
        self._graph.add_node(concept_id, attributes)

    def remove_concept(self, concept_id: str) -> bool:
        return self._graph.remove_node(concept_id)

    def get_concept(self, concept_id: str) -> dict[str, Any] | None:
        return self._graph.get_node(concept_id)

    def add_relation(
        self,
        source: str,
        target: str,
        relation_type: str,
        properties: dict[str, Any] | None = None,
    ) -> None:
        self._graph.add_edge(source, target, label=relation_type, properties=properties)

    def remove_relation(self, source: str, target: str, relation_type: str = "") -> int:
        return self._graph.remove_edges(source, target, label=relation_type)

    def query_relations(self, concept_id: str) -> list[dict[str, Any]]:
        return self._graph.get_neighbors(concept_id)

    def query_by_relation(self, relation_type: str) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for e in self._graph.edges:
            if e["label"] == relation_type:
                results.append(
                    {
                        "source": e["source"],
                        "target": e["target"],
                        "relation": e["label"],
                        "properties": e.get("properties", {}),
                    }
                )
        return results

    def infer_ancestors(self, concept_id: str, relation_type: str = "is_a") -> list[str]:
        ancestors: list[str] = []
        visited: set[str] = set()
        queue: list[str] = [concept_id]
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            for e in self._graph.edges:
                if e["target"] == current and e["label"] == relation_type and e["source"] not in visited:
                    ancestors.append(e["source"])
                    queue.append(e["source"])
        return ancestors

    def infer_descendants(self, concept_id: str, relation_type: str = "is_a") -> list[str]:
        descendants: list[str] = []
        visited: set[str] = set()
        queue: list[str] = [concept_id]
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            for e in self._graph.edges:
                if e["source"] == current and e["label"] == relation_type and e["target"] not in visited:
                    descendants.append(e["target"])
                    queue.append(e["target"])
        return descendants

    def size(self) -> tuple[int, int]:
        return self._graph.size()

    def clear(self) -> None:
        self._graph.clear()

    def to_dict(self) -> dict[str, Any]:
        return self._graph.to_dict()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SemanticNetwork:
        return cls(graph=KnowledgeGraph.from_dict(data))
