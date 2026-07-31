from __future__ import annotations

from typing import Any

from ...connector_template import ProviderConnector


class MongoDBConnector(ProviderConnector):
    """Connector for MongoDB databases (offline in-memory simulation)."""

    connector_type = "mongodb"
    display_name = "MongoDB"
    version = "1.0.0"

    def __init__(self) -> None:
        super().__init__()
        self.register_many(
            {
                "list_collections": lambda params: {"collections": ["events", "audit"]},
                "find": lambda params: self._query(params),
                "insert_one": lambda params: self._insert(params),
                "update_one": lambda params: self._update(params.get("id", ""), params.get("changes", {})),
                "delete_one": lambda params: self._delete(params.get("id", "")),
                "count": lambda params: len(self._records),
            }
        )

    def _query(self, params: dict[str, Any]) -> dict[str, Any]:
        self._require_connected()
        filters = params.get("filter")
        rows = self._all(filters)
        return {"documents": rows, "count": len(rows)}

    def _insert(self, params: dict[str, Any]) -> dict[str, Any]:
        self._require_connected()
        record = self._add(params.get("document", {}))
        return {"id": record["id"], "document": record}

    def _do_connect(self, config: Any) -> bool:
        return bool(config.config.get("uri") or config.config.get("host"))
