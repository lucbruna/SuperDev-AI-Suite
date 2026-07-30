from __future__ import annotations

import time
from typing import Any

from ..monitoring_models import MetricSample, MetricType


class ApiMetrics:
    """Metrics collector for API request/response lifecycle."""

    def __init__(self) -> None:
        self._request_count: int = 0
        self._error_count: int = 0
        self._status_codes: dict[int, int] = {}

    def record_request(self, status_code: int, duration_ms: float) -> list[MetricSample]:
        self._request_count += 1
        self._status_codes[status_code] = self._status_codes.get(status_code, 0) + 1
        if status_code >= 500:
            self._error_count += 1
        return [
            MetricSample("api_requests_total", 1.0, metric_type=MetricType.COUNTER),
            MetricSample("api_request_duration_ms", duration_ms, metric_type=MetricType.HISTOGRAM),
            MetricSample("api_errors_total", 1.0 if status_code >= 500 else 0.0, metric_type=MetricType.COUNTER),
            MetricSample("api_status_code", float(status_code), labels={"code": str(status_code)}, metric_type=MetricType.GAUGE),
        ]

    def snapshot(self) -> dict[str, Any]:
        return {
            "request_count": self._request_count,
            "error_count": self._error_count,
            "status_codes": dict(self._status_codes),
        }

    def reset(self) -> None:
        self._request_count = 0
        self._error_count = 0
        self._status_codes.clear()


__all__ = ["ApiMetrics"]
