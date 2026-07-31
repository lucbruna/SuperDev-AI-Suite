"""Sync engine."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class SyncEngine:
    def __init__(self) -> None:
        self._sources: Dict[str, Dict[str, Any]] = {}
        self._sync_log: List[Dict[str, Any]] = []
        self._started = False
    def start(self) -> None:
        self._started = True
    def register_source(self, source_id: str, name: str, source_type: str = "database") -> Dict[str, Any]:
        source = {"source_id": source_id, "name": name, "type": source_type, "last_sync": None, "status": "registered"}
        self._sources[source_id] = source
        return source
    def sync(self, source_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        if source_id not in self._sources:
            return {"error": "not_found"}
        self._sources[source_id]["last_sync"] = time.time()
        self._sources[source_id]["status"] = "synced"
        entry = {"source_id": source_id, "records": len(data), "timestamp": time.time()}
        self._sync_log.append(entry)
        return {"source_id": source_id, "synced": True, "records": len(data)}
    def get_status(self, source_id: str) -> Dict[str, Any]:
        return self._sources.get(source_id, {"error": "not_found"})
    def list_sources(self) -> List[Dict[str, Any]]:
        return list(self._sources.values())
    def get_log(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._sync_log[-limit:]
    def count(self) -> int:
        return len(self._sources)
    def is_running(self) -> bool:
        return self._started
