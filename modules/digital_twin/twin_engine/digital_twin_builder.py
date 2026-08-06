"""Twin model: the in-memory representation of a digital twin."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class TwinModel:
    """A named twin: entities keyed by id plus typed relationships."""

    name: str = "default"
    entities: dict[str, dict[str, object]] = field(default_factory=dict)
    relationships: list[dict[str, str]] = field(default_factory=list)
    meta: dict[str, object] = field(default_factory=dict)

    def add_entity(self, entity: dict[str, object]) -> None:
        self.entities[str(entity["id"])] = entity

    def add_relationship(self, source: str, target: str, kind: str) -> None:
        self.relationships.append(
            {"source": source, "target": target, "kind": kind}
        )

    def entity_ids(self) -> list[str]:
        return list(self.entities)

    def __len__(self) -> int:
        return len(self.entities)

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "entities": {k: dict(v) for k, v in self.entities.items()},
            "relationships": [dict(r) for r in self.relationships],
            "meta": dict(self.meta),
        }
