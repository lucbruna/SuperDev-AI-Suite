"""Sync engine."""

from __future__ import annotations

import time
from typing import Any


class SyncEngine:
    def __init__(self) -> None:
        self._sources: dict[str, dict[str, Any]] = {}
        self._sync_log: list[dict[str, Any]] = []
        self._started = False

    def start(self) -> None:
        self._started = True

    def register_source(self, source_id: str, name: str, source_type: str = "database") -> dict[str, Any]:
        source = {"source_id": source_id, "name": name, "type": source_type, "last_sync": None, "status": "registered"}
        self._sources[source_id] = source
        return source

    def sync(self, source_id: str, data: dict[str, Any]) -> dict[str, Any]:
        if source_id not in self._sources:
            return {"error": "not_found"}
        self._sources[source_id]["last_sync"] = time.time()
        self._sources[source_id]["status"] = "synced"
        entry = {"source_id": source_id, "records": len(data), "timestamp": time.time()}
        self._sync_log.append(entry)
        return {"source_id": source_id, "synced": True, "records": len(data)}

    def get_status(self, source_id: str) -> dict[str, Any]:
        return self._sources.get(source_id, {"error": "not_found"})

    def list_sources(self) -> list[dict[str, Any]]:
        return list(self._sources.values())

    def get_log(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._sync_log[-limit:]

    def count(self) -> int:
        return len(self._sources)

    def is_running(self) -> bool:
        return self._started
