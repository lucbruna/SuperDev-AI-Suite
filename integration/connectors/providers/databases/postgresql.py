from __future__ import annotations

from typing import Any

from ...connector_template import ProviderConnector


class PostgreSQLConnector(ProviderConnector):
    """Connector for PostgreSQL databases (offline in-memory simulation)."""

    connector_type = "postgresql"
    display_name = "PostgreSQL"
    version = "1.0.0"

    def __init__(self) -> None:
        super().__init__()
        self.register_many(
            {
                "list_tables": lambda params: {
                    "tables": ["users", "orders", "products"], "dialect": "postgresql"
                },
                "query": lambda params: self._query(params),
                "insert": lambda params: self._insert(params),
                "update": lambda params: self._update(params.get("id", ""), params.get("changes", {})),
                "delete": lambda params: self._delete(params.get("id", "")),
                "count": lambda params: len(self._records),
            }
        )

    def _query(self, params: dict[str, Any]) -> dict[str, Any]:
        self._require_connected()
        filters = params.get("filters")
        limit = int(params.get("limit", 100))
        rows = self._all(filters)[:limit]
        return {"rows": rows, "count": len(rows)}

    def _insert(self, params: dict[str, Any]) -> dict[str, Any]:
        self._require_connected()
        record = self._add(params.get("record", {}))
        return {"id": record["id"], "row": record}

    def _do_connect(self, config: Any) -> bool:
        host = config.config.get("host")
        return bool(host and config.config.get("database"))
