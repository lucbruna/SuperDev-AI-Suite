from __future__ import annotations

import json
import time
from typing import Any

from ..api_events import APIEventBus, APIEventType
from ..api_logger import APILogger
from ..api_metrics import APIMetrics


class Monitor:
    """System monitor collecting and reporting health, metrics, and events."""

    def __init__(
        self,
        metrics: APIMetrics | None = None,
        events: APIEventBus | None = None,
        logger: APILogger | None = None,
    ) -> None:
        self._metrics = metrics or APIMetrics()
        self._events = events
        self._logger = logger or APILogger("api.monitor")
        self._alert_handlers: list[Any] = []
        self._thresholds: dict[str, float] = {
            "error_rate": 0.05,
            "avg_latency_ms": 5000,
            "requests_per_second": 1000,
        }

    def set_threshold(self, metric: str, value: float) -> None:
        self._thresholds[metric] = value

    def register_alert_handler(self, handler: Any) -> None:
        self._alert_handlers.append(handler)

    def snapshot(self) -> dict[str, Any]:
        counters = self._metrics.get_counters()
        total_requests = counters.get("requests", 0)
        total_errors = counters.get("errors", 0)
        error_rate = total_errors / max(total_requests, 1)

        return {
            "timestamp": time.time(),
            "uptime_seconds": self._metrics.uptime_seconds,
            "total_requests": total_requests,
            "total_errors": total_errors,
            "error_rate": round(error_rate, 4),
            "active_connections": counters.get("ws.connections", 0) - counters.get("ws.disconnections", 0),
            "alerts": [h.to_dict() if hasattr(h, "to_dict") else str(h) for h in self._alert_handlers],
            "thresholds": dict(self._thresholds),
        }

    def check_alerts(self) -> list[dict[str, Any]]:
        alerts: list[dict[str, Any]] = []
        snap = self.snapshot()

        if snap["error_rate"] > self._thresholds["error_rate"]:
            alerts.append({
                "level": "warning",
                "metric": "error_rate",
                "value": snap["error_rate"],
                "threshold": self._thresholds["error_rate"],
            })

        for handler in self._alert_handlers:
            try:
                result = handler(snap)
                if result:
                    alerts.append(result)
            except Exception as e:
                self._logger.error("Alert handler error", error=str(e))

        return alerts

    def to_dict(self) -> dict[str, Any]:
        return {
            "monitor": "Monitor",
            "snapshot": self.snapshot(),
            "thresholds": dict(self._thresholds),
            "alert_handlers": len(self._alert_handlers),
        }
