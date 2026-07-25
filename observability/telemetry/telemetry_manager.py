import time
from typing import Any, Dict, List, Optional
from .exporters import ConsoleExporter, FileExporter, PrometheusExporter


class TelemetryManager:
    def __init__(self) -> None:
        self._events: List[Dict[str, Any]] = []
        self._users: Dict[str, Dict[str, Any]] = {}
        self._exporters: List[Any] = []

    def add_exporter(self, exporter: Any) -> None:
        self._exporters.append(exporter)

    def track_event(self, name: str, properties: Optional[Dict[str, Any]] = None) -> None:
        event = {
            "event": name,
            "properties": properties or {},
            "timestamp": time.time(),
        }
        self._events.append(event)
        for exporter in self._exporters:
            try:
                exporter.export(event)
            except Exception:
                pass

    def identify_user(self, user_id: str, traits: Optional[Dict[str, Any]] = None) -> None:
        self._users[user_id] = {
            "user_id": user_id,
            "traits": traits or {},
            "identified_at": time.time(),
        }

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self._users.get(user_id)

    def get_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self._events[-limit:]

    def flush(self) -> None:
        self._events.clear()
        self._users.clear()
