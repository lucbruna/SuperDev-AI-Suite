from __future__ import annotations

from typing import Any

from ...connector_template import ProviderConnector


class MySQLConnector(ProviderConnector):
    """Connector for MySQL databases (offline in-memory simulation)."""

    connector_type = "mysql"
    display_name = "MySQL"
    version = "1.0.0"

    def __init__(self) -> None:
        super().__init__()
        self.register_many(
            {
                "list_databases": lambda params: {"databases": ["app", "logs"]},
                "query": lambda params: self._query(params),
                "insert": lambda params: self._insert(params),
                "update": lambda params: self._update(params.get("id", ""), params.get("changes", {})),
                "delete": lambda params: self._delete(params.get("id", "")),
                "ping": lambda params: {"pong": True, "dialect": "mysql"},
            }
        )

    def _query(self, params: dict[str, Any]) -> dict[str, Any]:
        self._require_connected()
        filters = params.get("filters")
        rows = self._all(filters)
        return {"rows": rows, "count": len(rows)}

    def _insert(self, params: dict[str, Any]) -> dict[str, Any]:
        self._require_connected()
        record = self._add(params.get("record", {}))
        return {"id": record["id"], "row": record}

    def _do_connect(self, config: Any) -> bool:
        return bool(config.config.get("host") and config.config.get("database"))
