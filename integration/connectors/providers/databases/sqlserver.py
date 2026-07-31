from __future__ import annotations

from typing import Any

from ...connector_template import ProviderConnector


class SQLServerConnector(ProviderConnector):
    """Connector for SQL Server databases (offline in-memory simulation)."""

    connector_type = "sqlserver"
    display_name = "SQL Server"
    version = "1.0.0"

    def __init__(self) -> None:
        super().__init__()
        self.register_many(
            {
                "list_schemas": lambda params: {"schemas": ["dbo", "sales"]},
                "query": lambda params: self._query(params),
                "insert": lambda params: self._insert(params),
                "update": lambda params: self._update(params.get("id", ""), params.get("changes", {})),
                "delete": lambda params: self._delete(params.get("id", "")),
                "stored_procedure": lambda params: {"executed": params.get("name", ""), "ok": True},
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
        return bool(config.config.get("server") and config.config.get("database"))
