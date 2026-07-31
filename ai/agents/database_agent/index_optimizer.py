from __future__ import annotations

from typing import Any


class IndexOptimizer:
    """Manages and optimizes database indexes."""

    def __init__(self) -> None:
        self._indexes: dict[str, dict[str, Any]] = {}

    def add_index(
        self,
        name: str,
        table: str,
        columns: list[str],
        unique: bool = False,
    ) -> str:
        self._indexes[name] = {
            "name": name,
            "table": table,
            "columns": columns,
            "unique": unique,
        }
        return name

    def get_index(self, name: str) -> dict[str, Any] | None:
        return self._indexes.get(name)

    def remove_index(self, name: str) -> bool:
        if name in self._indexes:
            del self._indexes[name]
            return True
        return False

    def list_indexes(self, table: str | None = None) -> list[dict[str, Any]]:
        indexes = list(self._indexes.values())
        if table:
            indexes = [i for i in indexes if i["table"] == table]
        return indexes

    @property
    def index_count(self) -> int:
        return len(self._indexes)

    def analyze_index_usage(
        self,
        queries: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        unused = []
        for idx in self._indexes.values():
            used = False
            for q in queries:
                sql = q.get("sql", "").lower()
                for col in idx["columns"]:
                    if col.lower() in sql:
                        used = True
                        break
            if not used:
                unused.append({
                    "index": idx["name"],
                    "table": idx["table"],
                    "suggestion": "Consider removing unused index",
                    "impact": "Dropping may improve write performance",
                })
        return unused

    def to_dict(self) -> dict[str, Any]:
        return {
            "indexes": list(self._indexes.values()),
            "index_count": self.index_count,
        }
