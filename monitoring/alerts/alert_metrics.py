from __future__ import annotations

import time
from collections import Counter
from typing import Any

from ..monitoring_models import Alert


class AlertMetrics:
    """Tracks alert metrics and statistics."""

    def __init__(self) -> None:
        self._total_fired: int = 0
        self._total_resolved: int = 0
        self._firing_count: int = 0
        self._by_severity: Counter[str] = Counter()
        self._by_name: Counter[str] = Counter()
        self._last_alert_time: float = 0.0
        self._firing_alerts: dict[str, float] = {}

    def record_fired(self, alert: Alert) -> None:
        self._total_fired += 1
        self._firing_count += 1
        self._by_severity[alert.severity.value] += 1
        self._by_name[alert.name] += 1
        self._last_alert_time = time.time()
        self._firing_alerts[alert.name] = time.time()

    def record_resolved(self, alert_name: str) -> None:
        self._total_resolved += 1
        self._firing_count = max(0, self._firing_count - 1)
        self._firing_alerts.pop(alert_name, None)

    def snapshot(self) -> dict[str, Any]:
        return {
            "total_fired": self._total_fired,
            "total_resolved": self._total_resolved,
            "currently_firing": self._firing_count,
            "by_severity": dict(self._by_severity),
            "by_name": dict(self._by_name.most_common(20)),
            "last_alert_time": self._last_alert_time,
            "firing_alerts": list(self._firing_alerts.keys()),
            "average_alerts_per_minute": self._rate(),
        }

    def _rate(self) -> float:
        if not self._last_alert_time:
            return 0.0
        elapsed = time.time() - self._last_alert_time
        if elapsed < 1:
            return float(self._total_fired)
        return self._total_fired / (elapsed / 60)

    def reset(self) -> None:
        self.__init__()
