"""Data Platform Runtime — Runtime context for data platform operations."""

from datetime import datetime
from typing import Any

from .data_config import DataPlatformConfig


class DataPlatformRuntime:
    def __init__(self, config: DataPlatformConfig | None = None):
        self._config = config or DataPlatformConfig()
        self._start_time: datetime | None = None
        self._metrics: dict[str, Any] = {}

    def start(self) -> None:
        self._start_time = datetime.now()
        self._metrics["started_at"] = self._start_time.isoformat()

    def stop(self) -> None:
        self._metrics["stopped_at"] = datetime.now().isoformat()

    def record_metric(self, key: str, value: Any) -> None:
        self._metrics[key] = value

    def get_metric(self, key: str) -> Any | None:
        return self._metrics.get(key)

    def get_all_metrics(self) -> dict[str, Any]:
        return dict(self._metrics)

    @property
    def is_running(self) -> bool:
        return self._start_time is not None and "stopped_at" not in self._metrics

    @property
    def uptime_seconds(self) -> float:
        if not self._start_time:
            return 0.0
        end = datetime.now()
        return (end - self._start_time).total_seconds()
