"""SQL datasource ingestion."""

from __future__ import annotations

import sqlite3
from typing import Any, Iterable

from data_intelligence.data_models import SourceType
from data_intelligence.ingestion.base import BaseSource


class SqlSource(BaseSource):
    """Fetches rows from a SQL database.

    The default implementation supports ``sqlite3`` via a ``dsn`` path.
    Alternative engines are supported by passing ``connector`` (a callable
    that returns ``(rows, close)``).
    """

    source_type = SourceType.SQL

    def __init__(self, source_id: str, name: str, dsn: str | None = None,
                 query: str | None = None, connector: Any = None,
                 **config: Any) -> None:
        super().__init__(source_id, name, dsn=dsn, query=query,
                         connector=connector, **config)
        self.dsn = dsn
        self.query = query or "SELECT 1"

    def fetch(self, source: Any = None) -> Iterable[dict[str, Any]]:  # noqa: ARG002
        if self.config.get("connector") is not None:
            return self._fetch_custom()
        if not self.dsn:
            raise RuntimeError("SqlSource requires dsn or connector")
        conn = sqlite3.connect(self.dsn)
        try:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(self.query).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def _fetch_custom(self) -> list[dict[str, Any]]:
        connector = self.config["connector"]
        rows, close = connector(self)
        try:
            return [dict(row) for row in rows]
        finally:
            if callable(close):
                close()
