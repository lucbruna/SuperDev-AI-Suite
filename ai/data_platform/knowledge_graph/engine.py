"""Knowledge Graph engine."""
import uuid

from .models import Entity, GraphQuery, KnowledgePath, Relation


class KnowledgeGraphEngine:
    def __init__(self):
        self._entities: dict[str, Entity] = {}
        self._relations: dict[str, Relation] = {}
        self._adjacency: dict[str, list[str]] = {}

    def add_entity(self, entity: Entity) -> Entity:
        self._entities[entity.entity_id] = entity
        return entity

    def get_entity(self, entity_id: str) -> Entity | None:
        return self._entities.get(entity_id)

    def add_relation(self, relation: Relation) -> Relation:
        self._relations[relation.relation_id] = relation
        self._adjacency.setdefault(relation.source_id, []).append(relation.relation_id)
        self._adjacency.setdefault(relation.target_id, []).append(relation.relation_id)
        return relation

    def get_relation(self, relation_id: str) -> Relation | None:
        return self._relations.get(relation_id)

    def get_entity_relations(self, entity_id: str) -> list[Relation]:
        rel_ids = self._adjacency.get(entity_id, [])
        return [self._relations[rid] for rid in rel_ids if rid in self._relations]

    def get_neighbors(self, entity_id: str, max_depth: int = 1) -> list[Entity]:
        visited: set[str] = set()
        result: list[Entity] = []
        queue = [(entity_id, 0)]
        while queue:
            eid, depth = queue.pop(0)
            if eid in visited or depth > max_depth:
                continue
            visited.add(eid)
            if eid != entity_id:
                entity = self._entities.get(eid)
                if entity:
                    result.append(entity)
            for rel in self.get_entity_relations(eid):
                next_id = rel.target_id if rel.source_id == eid else rel.source_id
                if next_id not in visited:
                    queue.append((next_id, depth + 1))
        return result

    def find_path(self, source_id: str, target_id: str, max_depth: int = 5) -> KnowledgePath | None:
        visited: set[str] = set()
        queue = [(source_id, [source_id], [])]
        while queue:
            eid, path, rel_path = queue.pop(0)
            if eid == target_id and len(path) > 1:
                return KnowledgePath(
                    path_id=str(uuid.uuid4())[:8],
                    entities=path,
                    relations=rel_path,
                    score=1.0 / len(path),
                )
            if eid in visited or len(path) > max_depth:
                continue
            visited.add(eid)
            for rel in self.get_entity_relations(eid):
                next_id = rel.target_id if rel.source_id == eid else rel.source_id
                if next_id not in visited:
                    queue.append((next_id, path + [next_id], rel_path + [rel.relation_id]))
        return None

    def search_entities(self, query: GraphQuery) -> list[Entity]:
        entities = list(self._entities.values())
        if query.entity_type:
            entities = [e for e in entities if e.entity_type == query.entity_type]
        return entities[:query.limit]

    def get_all_entities(self) -> list[Entity]:
        return list(self._entities.values())

    def get_all_relations(self) -> list[Relation]:
        return list(self._relations.values())

    def get_entity_count(self) -> int:
        return len(self._entities)

    def get_relation_count(self) -> int:
        return len(self._relations)

    def get_stats(self) -> dict:
        return {
            "entities": len(self._entities),
            "relations": len(self._relations),
            "entity_types": len(set(e.entity_type.value for e in self._entities.values())),
            "relation_types": len(set(r.relation_type.value for r in self._relations.values())),
        }
