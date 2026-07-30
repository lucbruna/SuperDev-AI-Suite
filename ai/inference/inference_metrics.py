from __future__ import annotations

import time
from typing import Any


class InferenceMetrics:
    """Metrics collection for inference operations."""

    def __init__(self) -> None:
        self._records: list[dict[str, Any]] = []

    async def record(self, strategy: str, result: Any) -> None:
        self._records.append({
            "strategy": strategy,
            "timestamp": time.time(),
            "result_type": type(result).__name__,
        })

    async def summary(self, strategy: str | None = None) -> dict[str, Any]:
        filtered = self._records
        if strategy:
            filtered = [r for r in filtered if r["strategy"] == strategy]
        return {
            "total_calls": len(filtered),
            "strategies": list({r["strategy"] for r in filtered}),
            "last_call": filtered[-1]["timestamp"] if filtered else None,
        }

    async def average_latency(self, strategy: str | None = None) -> float:
        return 0.0
