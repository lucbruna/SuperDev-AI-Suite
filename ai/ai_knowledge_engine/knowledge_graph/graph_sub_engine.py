"""Knowledge graph subsystem engine — Entity-relationship knowledge graph."""
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Entity:
    entity_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    entity_type: str = "concept"
    properties: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Relationship:
    relationship_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    source_id: str = ""
    target_id: str = ""
    relationship_type: str = "related_to"
    weight: float = 1.0
    properties: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class GraphPath:
    path_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    nodes: list[str] = field(default_factory=list)
    edges: list[str] = field(default_factory=list)
    length: int = 0


class GraphSubEngine:
    def __init__(self):
        self._entities: dict[str, Entity] = {}
        self._relationships: dict[str, Relationship] = {}
        self._adjacency: dict[str, list[str]] = {}
        self._reverse_adjacency: dict[str, list[str]] = {}

    def add_entity(self, name: str, entity_type: str = "concept", properties: dict[str, Any] | None = None) -> Entity:
        entity = Entity(name=name, entity_type=entity_type, properties=properties or {})
        self._entities[entity.entity_id] = entity
        if entity.entity_id not in self._adjacency:
            self._adjacency[entity.entity_id] = []
        if entity.entity_id not in self._reverse_adjacency:
            self._reverse_adjacency[entity.entity_id] = []
        return entity

    def get_entity(self, entity_id: str) -> Entity | None:
        return self._entities.get(entity_id)

    def find_entity_by_name(self, name: str) -> Entity | None:
        for e in self._entities.values():
            if e.name == name:
                return e
        return None

    def add_relationship(self, source_id: str, target_id: str, relationship_type: str = "related_to", weight: float = 1.0) -> Relationship | None:
        if source_id not in self._entities or target_id not in self._entities:
            return None
        rel = Relationship(source_id=source_id, target_id=target_id, relationship_type=relationship_type, weight=weight)
        self._relationships[rel.relationship_id] = rel
        self._adjacency.setdefault(source_id, []).append(rel.relationship_id)
        self._reverse_adjacency.setdefault(target_id, []).append(rel.relationship_id)
        return rel

    def get_relationship(self, relationship_id: str) -> Relationship | None:
        return self._relationships.get(relationship_id)

    def get_neighbors(self, entity_id: str) -> list[Entity]:
        neighbors = []
        for rel_id in self._adjacency.get(entity_id, []):
            rel = self._relationships.get(rel_id)
            if rel:
                neighbor = self._entities.get(rel.target_id)
                if neighbor:
                    neighbors.append(neighbor)
        return neighbors

    def get_reverse_neighbors(self, entity_id: str) -> list[Entity]:
        neighbors = []
        for rel_id in self._reverse_adjacency.get(entity_id, []):
            rel = self._relationships.get(rel_id)
            if rel:
                neighbor = self._entities.get(rel.source_id)
                if neighbor:
                    neighbors.append(neighbor)
        return neighbors

    def find_path(self, source_id: str, target_id: str, max_depth: int = 5) -> GraphPath | None:
        if source_id not in self._entities or target_id not in self._entities:
            return None
        visited: set[str] = set()
        queue = [(source_id, [source_id], [])]
        visited.add(source_id)
        while queue:
            current, path_nodes, path_edges = queue.pop(0)
            if current == target_id:
                return GraphPath(nodes=path_nodes, edges=path_edges, length=len(path_edges))
            if len(path_nodes) > max_depth:
                continue
            for rel_id in self._adjacency.get(current, []):
                rel = self._relationships.get(rel_id)
                if rel and rel.target_id not in visited:
                    visited.add(rel.target_id)
                    queue.append((rel.target_id, path_nodes + [rel.target_id], path_edges + [rel_id]))
        return None

    def get_entity_relationships(self, entity_id: str) -> list[Relationship]:
        rels = []
        for rel_id in self._adjacency.get(entity_id, []):
            rel = self._relationships.get(rel_id)
            if rel:
                rels.append(rel)
        for rel_id in self._reverse_adjacency.get(entity_id, []):
            rel = self._relationships.get(rel_id)
            if rel:
                rels.append(rel)
        return rels

    def delete_entity(self, entity_id: str) -> bool:
        if entity_id not in self._entities:
            return False
        for rel_id in self._adjacency.get(entity_id, []):
            self._relationships.pop(rel_id, None)
        for rel_id in self._reverse_adjacency.get(entity_id, []):
            self._relationships.pop(rel_id, None)
        self._adjacency.pop(entity_id, None)
        self._reverse_adjacency.pop(entity_id, None)
        del self._entities[entity_id]
        return True

    def get_subgraph(self, entity_id: str, depth: int = 2) -> dict[str, Any]:
        visited: set[str] = set()
        entities = []
        relationships = []
        queue = [(entity_id, 0)]
        visited.add(entity_id)
        while queue:
            current, d = queue.pop(0)
            entity = self._entities.get(current)
            if entity:
                entities.append({"id": entity.entity_id, "name": entity.name, "type": entity.entity_type})
            if d >= depth:
                continue
            for rel_id in self._adjacency.get(current, []):
                rel = self._relationships.get(rel_id)
                if rel:
                    relationships.append({"source": rel.source_id, "target": rel.target_id, "type": rel.relationship_type})
                    if rel.target_id not in visited:
                        visited.add(rel.target_id)
                        queue.append((rel.target_id, d + 1))
        return {"entities": entities, "relationships": relationships}

    def get_stats(self) -> dict:
        return {
            "total_entities": len(self._entities),
            "total_relationships": len(self._relationships),
            "entity_types": len(set(e.entity_type for e in self._entities.values())),
            "relationship_types": len(set(r.relationship_type for r in self._relationships.values())),
        }
