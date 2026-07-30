from __future__ import annotations

import math
from typing import Any


class MetricsCalculator:
    """Computes aggregate metrics from response data."""

    @staticmethod
    def compute(response_times: list[float]) -> dict[str, float]:
        if not response_times:
            return {"p50": 0.0, "p95": 0.0, "p99": 0.0, "mean": 0.0, "min": 0.0, "max": 0.0}

        sorted_times = sorted(response_times)
        n = len(sorted_times)

        return {
            "p50": sorted_times[max(0, int(n * 0.5) - 1)],
            "p95": sorted_times[max(0, int(n * 0.95) - 1)],
            "p99": sorted_times[max(0, int(n * 0.99) - 1)],
            "mean": sum(sorted_times) / n,
            "min": sorted_times[0],
            "max": sorted_times[-1],
        }

    @staticmethod
    def compute_token_efficiency(tokens_prompt: int, tokens_completion: int) -> float:
        total = tokens_prompt + tokens_completion
        if total == 0:
            return 0.0
        return tokens_completion / total

    def to_dict(self) -> dict[str, Any]:
        return {
            "methods": ["compute", "compute_token_efficiency"],
        }
