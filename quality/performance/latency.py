"""Deep-dive latency analysis — percentiles, timing, classification.

Complementa o ``PerformanceEngine.latency`` com:

- ``LatencyAnalyzer`` — coleta amostras, calcula p50/p95/p99, jitter e
  classifica a latência contra um alvo (critical/warning/ok);
- ``time_operation`` — helper para medir uma chamada única.
"""

from __future__ import annotations

import math
import statistics
import time
from collections.abc import Callable
from typing import Any


def time_operation(operation: Callable[[], Any]) -> float:
    """Run a callable once and return its wall-clock duration in ms."""
    started = time.perf_counter()
    operation()
    return (time.perf_counter() - started) * 1000


def percentile(values: list[float], pct: float) -> float:
    """Nearest-rank percentile of a sorted/unsorted sample (0 <= pct <= 100)."""
    if not values:
        return 0.0
    ordered = sorted(values)
    rank = max(1, min(len(ordered), math.ceil(pct / 100 * len(ordered))))
    return ordered[rank - 1]


class LatencyAnalyzer:
    """Latency sampling, percentiles and target classification.

    Uso:
        analyzer = LatencyAnalyzer(target_ms=200.0)
        analyzer.record(time_operation(operation))
        stats = analyzer.summary()   # avg/p50/p95/p99/min/max/jitter/samples
        analyzer.verdict()           # {"level": "ok"|"warning"|"critical", ...}
    """

    def __init__(self, target_ms: float = 200.0, engine: Any | None = None) -> None:
        self.target_ms = float(target_ms)
        self.engine = engine
        self._samples: list[float] = []
        self._labels: dict[str, str] = {}

    # -- sampling ------------------------------------------------------------

    def record(self, duration_ms: float) -> None:
        self._samples.append(duration_ms)

    def run(self, operation: Callable[[], Any], samples: int = 100) -> dict[str, Any]:
        """Measure a callable N times, record everything and return summary."""
        for _ in range(max(1, samples)):
            self.record(time_operation(operation))
        return self.summary()

    def reset(self) -> None:
        self._samples.clear()

    def set_labels(self, **labels: str) -> None:
        self._labels.update(labels)

    # -- statistics ----------------------------------------------------------

    def count(self) -> int:
        return len(self._samples)

    def average(self) -> float:
        return round(statistics.mean(self._samples), 2) if self._samples else 0.0

    def p50(self) -> float:
        return round(percentile(self._samples, 50), 2)

    def p95(self) -> float:
        return round(percentile(self._samples, 95), 2)

    def p99(self) -> float:
        return round(percentile(self._samples, 99), 2)

    def minimum(self) -> float:
        return round(min(self._samples), 2) if self._samples else 0.0

    def maximum(self) -> float:
        return round(max(self._samples), 2) if self._samples else 0.0

    def jitter(self) -> float:
        """Variation = (max - min) / mean; 0 when there is a single sample."""
        if len(self._samples) < 2:
            return 0.0
        mean = statistics.mean(self._samples)
        if mean == 0:
            return 0.0
        return round((max(self._samples) - min(self._samples)) / mean, 4)

    def summary(self) -> dict[str, Any]:
        return {
            "samples": self.count(),
            "avg_ms": self.average(),
            "p50_ms": self.p50(),
            "p95_ms": self.p95(),
            "p99_ms": self.p99(),
            "min_ms": self.minimum(),
            "max_ms": self.maximum(),
            "jitter": self.jitter(),
        }

    # -- classification ------------------------------------------------------

    def verdict(self) -> dict[str, Any]:
        """Classify latency against the target.

        Regras:
            ok       -> p50 <= target
            warning  -> p50 <= target e p95 <= target * 2
            critical -> caso contrário (ou p50 > target)
        """
        p50 = self.p50()
        p95 = self.p95()
        if p50 <= self.target_ms and p95 <= self.target_ms * 1.5:
            level = "ok"
        elif p50 <= self.target_ms:
            level = "warning"
        else:
            level = "critical"
        result = {
            "level": level,
            "target_ms": self.target_ms,
            "p50_ms": p50,
            "p95_ms": p95,
            "within_target": p50 <= self.target_ms,
        }
        if self.engine is not None:
            self.engine.metrics.gauge("performance.latency_p50", p50, labels=self._labels)
            self.engine.metrics.increment("performance.latency_verdicts")
        return result

    def is_within_target(self) -> bool:
        return self.verdict()["within_target"]


__all__ = ["LatencyAnalyzer", "percentile", "time_operation"]
