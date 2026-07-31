from __future__ import annotations

import math
import statistics
from typing import Any

from ..data_models import AnalyticsResult, DataRecord


class AnalyticsEngine:
    """Intelligent analytics — descriptive, diagnostic, predictive, prescriptive,
    correlation, segmentation, patterns."""

    def __init__(self, engine: Any) -> None:
        self.engine = engine
        self.config = engine.config.analytics
        self._results: dict[str, AnalyticsResult] = {}
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True

    async def shutdown(self) -> None:
        self._initialized = False

    # -- descriptive ---------------------------------------------------------

    def descriptive(self, records: list[DataRecord], field: str | None = None) -> dict[str, Any]:
        values = [
            r.data[field] for r in records
            if field and isinstance(r.data.get(field), (int, float))
        ]
        if not values:
            return {"count": len(records), "field": field or "all"}
        return {
            "count": len(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "stdev": statistics.pstdev(values) if len(values) > 1 else 0.0,
            "min": min(values),
            "max": max(values),
            "sum": sum(values),
        }

    # -- diagnostic ----------------------------------------------------------

    def diagnostic(self, records: list[DataRecord]) -> dict[str, Any]:
        by_source: dict[str, int] = {}
        by_quality: dict[str, int] = {}
        for record in records:
            by_source[record.source] = by_source.get(record.source, 0) + 1
            by_quality[record.quality.value] = by_quality.get(record.quality.value, 0) + 1
        return {"by_source": by_source, "by_quality": by_quality}

    # -- correlation ---------------------------------------------------------

    def correlation(self, records: list[DataRecord], x: str, y: str) -> float:
        pairs = [
            (r.data[x], r.data[y])
            for r in records
            if isinstance(r.data.get(x), (int, float)) and isinstance(r.data.get(y), (int, float))
        ]
        if len(pairs) < 2:
            return 0.0
        xs = [p[0] for p in pairs]
        ys = [p[1] for p in pairs]
        mx, my = statistics.mean(xs), statistics.mean(ys)
        sxy = sum((a - mx) * (b - my) for a, b in pairs)
        sxx = sum((a - mx) ** 2 for a in xs)
        syy = sum((b - my) ** 2 for b in ys)
        if sxx == 0 or syy == 0:
            return 0.0
        return sxy / math.sqrt(sxx * syy)

    # -- segmentation --------------------------------------------------------

    def segmentation(self, records: list[DataRecord], field: str) -> dict[str, list[DataRecord]]:
        segments: dict[str, list[DataRecord]] = {}
        for record in records:
            key = str(record.data.get(field, "unknown"))
            segments.setdefault(key, []).append(record)
        return segments

    # -- pattern detection ---------------------------------------------------

    def detect_patterns(self, records: list[DataRecord], field: str) -> dict[str, Any]:
        values = [
            r.data[field] for r in records
            if isinstance(r.data.get(field), (int, float))
        ]
        if not values:
            return {"trend": "insufficient_data", "volatility": 0.0}
        mean = statistics.mean(values)
        stdev = statistics.pstdev(values) if len(values) > 1 else 0.0
        trend = "increasing" if values[-1] > values[0] else ("decreasing" if values[-1] < values[0] else "stable")
        return {
            "trend": trend,
            "volatility": stdev / mean if mean else 0.0,
            "peak": max(values),
            "trough": min(values),
        }

    async def analyze(
        self,
        kind: str,
        records: list[DataRecord],
        options: dict[str, Any] | None = None,
    ) -> AnalyticsResult:
        options = options or {}
        field = options.get("field")
        if kind == "descriptive":
            result: dict[str, Any] = self.descriptive(records, field)
        elif kind == "diagnostic":
            result = self.diagnostic(records)
        elif kind == "correlation":
            result = {"correlation": self.correlation(records, options.get("x", "x"), options.get("y", "y"))}
        elif kind == "segmentation":
            segments = self.segmentation(records, field or "segment")
            result = {"segments": {k: len(v) for k, v in segments.items()}}
        elif kind == "patterns":
            result = self.detect_patterns(records, field or "value")
        else:
            result = self.descriptive(records, field)

        analysis = AnalyticsResult(kind=kind, results=result)
        self._results[analysis.analysis_id] = analysis
        self.engine.metrics.increment("analytics.analyses")
        return analysis

    def status(self) -> dict[str, Any]:
        return {
            "initialized": self._initialized,
            "analyses": len(self._results),
        }


__all__ = ["AnalyticsEngine"]
