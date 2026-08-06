"""Analytics over a twin model: structural statistics."""
from __future__ import annotations

from dataclasses import dataclass

from modules.digital_twin.config.constants import ENTITY_TYPES
from modules.digital_twin.twin_engine.digital_twin_builder import TwinModel


@dataclass(slots=True)
class TwinAnalysis:
    """Structural statistics computed from a twin model."""

    entity_count: int
    relationship_count: int
    types: dict[str, int]
    relations: dict[str, int]
    density: float  # relationship-to-entity ratio
    connected_entities: set[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "entity_count": self.entity_count,
            "relationship_count": self.relationship_count,
            "types": dict(self.types),
            "relations": dict(self.relations),
            "density": self.density,
            "connected_entities": sorted(self.connected_entities),
        }


class TwinAnalyzer:
    """Computes deterministic structural statistics of a twin."""

    def __init__(self, entity_types: tuple[str, ...] = ENTITY_TYPES) -> None:
        self._entity_types = entity_types

    def analyze(self, model: TwinModel) -> TwinAnalysis:
        types: dict[str, int] = {t: 0 for t in self._entity_types}
        for entity in model.entities.values():
            etype = str(entity.get("type", ""))
            types[etype] = types.get(etype, 0) + 1

        relations: dict[str, int] = {}
        connected: set[str] = set()
        for rel in model.relationships:
            kind = str(rel.get("kind", ""))
            relations[kind] = relations.get(kind, 0) + 1
            connected.add(str(rel.get("source", "")))
            connected.add(str(rel.get("target", "")))

        entity_count = len(model)
        rel_count = len(model.relationships)
        density = (rel_count / entity_count) if entity_count else 0.0
        return TwinAnalysis(
            entity_count=entity_count,
            relationship_count=rel_count,
            types={k: v for k, v in types.items() if v},
            relations=relations,
            density=round(density, 4),
            connected_entities=connected,
        )
