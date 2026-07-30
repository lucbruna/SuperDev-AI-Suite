from __future__ import annotations

import datetime
import json
import os
import time
from dataclasses import dataclass, field
from typing import Any, Literal

from ..monitoring_models import Alert, AlertSeverity, AlertStatus


@dataclass
class AlertHistoryEntry:
    timestamp: float = 0.0
    alert_name: str = ""
    severity: str = ""
    status: str = ""
    value: float = 0.0
    message: str = ""


class AlertHistory:
    """Persistent history of alert state transitions."""

    def __init__(self, storage_path: str = "alerts_history.json") -> None:
        self._path = storage_path
        self._entries: list[AlertHistoryEntry] = []
        self._load()

    def record(self, alert: Alert, event: str = "fired") -> None:
        entry = AlertHistoryEntry(
            timestamp=time.time(),
            alert_name=alert.name,
            severity=alert.severity.value,
            status=event,
            value=alert.value,
            message=alert.message,
        )
        self._entries.append(entry)
        self._save()

    def query(
        self,
        alert_name: str = "",
        severity: str = "",
        status: str = "",
        start_time: float = 0.0,
        end_time: float = 0.0,
        limit: int = 100,
    ) -> list[AlertHistoryEntry]:
        results = list(self._entries)

        if alert_name:
            results = [e for e in results if alert_name in e.alert_name]
        if severity:
            results = [e for e in results if e.severity == severity]
        if status:
            results = [e for e in results if e.status == status]
        if start_time:
            results = [e for e in results if e.timestamp >= start_time]
        if end_time:
            results = [e for e in results if e.timestamp <= end_time]

        results.sort(key=lambda e: e.timestamp, reverse=True)
        return results[:limit]

    def count_by_severity(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for entry in self._entries:
            counts[entry.severity] = counts.get(entry.severity, 0) + 1
        return counts

    def count_by_status(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for entry in self._entries:
            counts[entry.status] = counts.get(entry.status, 0) + 1
        return counts

    def clear(self) -> None:
        self._entries.clear()
        self._save()

    def _save(self) -> None:
        try:
            data = [
                {
                    "timestamp": e.timestamp,
                    "alert_name": e.alert_name,
                    "severity": e.severity,
                    "status": e.status,
                    "value": e.value,
                    "message": e.message,
                }
                for e in self._entries
            ]
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except OSError:
            pass

    def _load(self) -> None:
        if not os.path.exists(self._path):
            return
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._entries = [
                AlertHistoryEntry(**item) for item in data
            ]
        except (OSError, json.JSONDecodeError):
            pass
