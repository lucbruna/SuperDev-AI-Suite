"""Database adapter: deterministic, in-memory persistence abstraction."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class DatabaseAdapter:
    """JSON-serializable storage with namespaced collections.

    No external database is required; anything stored here is fully
    deterministic and inspectable via :meth:`snapshot`.
    """

    collections: dict[str, dict[str, Any]] = field(default_factory=dict)

    def insert(self, collection: str, key: str, document: dict[str, Any]) -> None:
        self.collections.setdefault(collection, {})[key] = document

    def get(self, collection: str, key: str) -> dict[str, Any] | None:
        return self.collections.get(collection, {}).get(key)

    def delete(self, collection: str, key: str) -> None:
        self.collections.get(collection, {}).pop(key, None)

    def list(self, collection: str) -> list[dict[str, Any]]:
        return list(self.collections.get(collection, {}).values())

    def snapshot(self) -> dict[str, Any]:
        return json.loads(json.dumps(self.collections))
