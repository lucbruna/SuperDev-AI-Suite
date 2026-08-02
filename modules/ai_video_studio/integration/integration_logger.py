"""Integration logger — bounded in-memory structured log of integration activity."""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

VALID_LEVELS = ("debug", "info", "warning", "error")


@dataclass
class LogEntry:
    ts: str
    level: str
    service: str
    message: str
    payload: dict[str, Any] = field(default_factory=dict)


class IntegrationLogger:
    """Ring-buffer structured logger, also fed by event-bus traffic."""

    def __init__(self, max_entries: int = 500) -> None:
        from modules.ai_video_studio.integration.event_bus import get_event_bus

        self._entries: deque[LogEntry] = deque(maxlen=max_entries)
        self._bus = get_event_bus()
        self._bus.subscribe("integration.log", self._on_log_event)
        self._bus.subscribe("*", self._on_any_event)

    async def _on_log_event(self, event_type: str, payload: dict[str, Any]) -> None:
        self.log(
            service=str(payload.get("service", "integration")),
            message=str(payload.get("message", "")),
            level=str(payload.get("level", "info")),
            payload={k: v for k, v in payload.items() if k not in ("service", "message", "level")},
        )

    async def _on_any_event(self, event_type: str, payload: dict[str, Any]) -> None:
        if event_type == "integration.log":
            return  # already logged above
        # Compact payload to keys only so huge event bodies never flood the log.
        self.log(
            service="event_bus",
            message=f"event {event_type}",
            level="debug",
            payload={"keys": sorted(payload)},
        )

    def log(
        self,
        service: str,
        message: str,
        *,
        level: str = "info",
        payload: dict[str, Any] | None = None,
    ) -> None:
        if level not in VALID_LEVELS:
            level = "info"
        self._entries.append(
            LogEntry(
                ts=datetime.now(UTC).isoformat(),
                level=level,
                service=service,
                message=message,
                payload=payload or {},
            )
        )

    def entries(self, limit: int = 100, level: str | None = None) -> list[dict[str, Any]]:
        """Most-recent entries, newest first, optionally filtered by level."""
        result = list(self._entries)[::-1]
        if level:
            result = [e for e in result if e.level == level]
        return [self._to_dict(e) for e in result[:limit]]

    def stats(self) -> dict[str, Any]:
        counts: dict[str, int] = {}
        for e in self._entries:
            counts[e.level] = counts.get(e.level, 0) + 1
        return {
            "total": len(self._entries),
            "by_level": {lvl: counts.get(lvl, 0) for lvl in VALID_LEVELS},
            "reported_at": datetime.now(UTC).isoformat(),
        }

    @staticmethod
    def _to_dict(e: LogEntry) -> dict[str, Any]:
        return {
            "ts": e.ts,
            "level": e.level,
            "service": e.service,
            "message": e.message,
            "payload": e.payload,
        }


_logger: IntegrationLogger | None = None


def get_integration_logger() -> IntegrationLogger:
    """Process-wide singleton logger."""
    global _logger
    if _logger is None:
        _logger = IntegrationLogger()
    return _logger
