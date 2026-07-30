from __future__ import annotations

import time
from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from ..monitoring_models import Alert, AlertSeverity


@dataclass
class AlertGroup:
    name: str = ""
    count: int = 0
    severity: AlertSeverity = AlertSeverity.INFO
    first_seen: float = 0.0
    last_seen: float = 0.0
    alerts: list[Alert] = field(default_factory=list)


class AlertAggregator:
    """Aggregates similar alerts into groups within a time window."""

    def __init__(self, window_seconds: float = 300.0) -> None:
        self._window = window_seconds
        self._groups: dict[str, AlertGroup] = {}

    def add(self, alert: Alert) -> AlertGroup | None:
        group_key = self._group_key(alert)
        now = time.time()

        if group_key in self._groups:
            group = self._groups[group_key]
            if (now - group.last_seen) < self._window:
                group.count += 1
                group.last_seen = now
                group.alerts.append(alert)
                return group
            else:
                del self._groups[group_key]

        group = AlertGroup(
            name=alert.name,
            count=1,
            severity=alert.severity,
            first_seen=now,
            last_seen=now,
            alerts=[alert],
        )
        self._groups[group_key] = group
        return group

    def _group_key(self, alert: Alert) -> str:
        return f"{alert.name}:{alert.severity.value}"

    def get_groups(self) -> list[AlertGroup]:
        self._prune()
        return list(self._groups.values())

    def get_group(self, name: str) -> AlertGroup | None:
        for group in self._groups.values():
            if group.name == name:
                return group
        return None

    def summary(self) -> dict[str, Any]:
        self._prune()
        return {
            "total_groups": len(self._groups),
            "severity_counts": dict(
                Counter(g.severity.value for g in self._groups.values())
            ),
            "groups": [
                {
                    "name": g.name,
                    "count": g.count,
                    "severity": g.severity.value,
                    "first_seen": g.first_seen,
                    "last_seen": g.last_seen,
                }
                for g in self._groups.values()
            ],
        }

    def _prune(self) -> None:
        now = time.time()
        expired = [
            k for k, v in self._groups.items()
            if (now - v.last_seen) > self._window
        ]
        for k in expired:
            del self._groups[k]

    def clear(self) -> None:
        self._groups.clear()
