"""TwinEntity: a digital representation of a physical/system entity."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TwinEntity:
    entity_id: str
    name: str = ""
    attributes: dict[str, Any] = field(default_factory=dict)
    state: dict[str, Any] = field(default_factory=dict)

    def set_state(self, **values: Any) -> None:
        self.state.update(values)

    def get(self, key: str, default: Any = None) -> Any:
        return self.state.get(key, default)

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "name": self.name,
            "attributes": dict(self.attributes),
            "state": dict(self.state),
        }
