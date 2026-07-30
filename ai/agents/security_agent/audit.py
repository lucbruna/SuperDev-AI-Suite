from __future__ import annotations

from typing import Any
from datetime import datetime, timezone


class Audit:
    """Audit logging for security events."""

    def __init__(self) -> None:
        self._events: dict[str, dict[str, Any]] = {}

    def log_event(
        self,
        event_type: str,
        actor: str,
        resource: str,
        result: str,
    ) -> str:
        eid = f"evt_{len(self._events) + 1:04d}"
        self._events[eid] = {
            "id": eid,
            "type": event_type,
            "actor": actor,
            "resource": resource,
            "result": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        return eid

    def get_event(self, event_id: str) -> dict[str, Any] | None:
        return self._events.get(event_id)

    def list_events(self, event_type: str | None = None) -> list[dict[str, Any]]:
        events = list(self._events.values())
        if event_type:
            events = [e for e in events if e["type"] == event_type]
        return sorted(events, key=lambda e: e["timestamp"], reverse=True)

    @property
    def event_count(self) -> int:
        return len(self._events)

    def search(self, query: str) -> list[dict[str, Any]]:
        q = query.lower()
        return [
            e for e in self._events.values()
            if q in e["type"].lower() or q in e["actor"].lower() or q in e["resource"].lower()
        ]

    def generate_audit_report(
        self,
        start: str | None = None,
        end: str | None = None,
    ) -> str:
        events = self.list_events()
        lines = ["# Audit Report", "=" * 40, ""]
        for e in events:
            lines.append(f"[{e['timestamp']}] {e['type']} | {e['actor']} -> {e['resource']} : {e['result']}")
        lines.append(f"\n---\nTotal events: {len(events)}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        return {
            "events": list(self._events.values()),
            "event_count": self.event_count,
        }
