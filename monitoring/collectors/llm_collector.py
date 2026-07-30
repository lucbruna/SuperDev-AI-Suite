from __future__ import annotations

import time
from typing import Any


class LlmCollector:
    """Collects LLM usage and latency metrics."""

    def __init__(self) -> None:
        self._request_count = 0
        self._total_latency = 0.0
        self._total_tokens = 0
        self._error_count = 0

    def record_request(
        self, latency: float, tokens: int = 0, error: bool = False
    ) -> None:
        self._request_count += 1
        self._total_latency += latency
        self._total_tokens += tokens
        if error:
            self._error_count += 1

    def collect(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "request_count": self._request_count,
            "total_latency": round(self._total_latency, 3),
            "total_tokens": self._total_tokens,
            "error_count": self._error_count,
            "timestamp": time.time(),
        }
        if self._request_count > 0:
            data["avg_latency"] = round(
                self._total_latency / self._request_count, 3
            )
        return data
