from __future__ import annotations

import statistics
from typing import Any

from ..data_models import DataRecord


class DescriptiveAnalyzer:
    """Descriptive statistics toolkit.

    Provides the classic descriptive-analysis primitives used by the
    AnalyticsEngine: central tendency, dispersion, quantiles, distribution
    shape (skewness / kurtosis), frequency histograms and per-record
    summaries. All methods are stdlib-only and operate on ``list[float]``.
    """

    def __init__(self, engine: Any | None = None) -> None:
        self.engine = engine
        self._summaries: dict[str, dict[str, Any]] = {}

    # -- central tendency ----------------------------------------------------

    @staticmethod
    def mean(values: list[float]) -> float:
        return statistics.mean(values) if values else 0.0

    @staticmethod
    def median(values: list[float]) -> float:
        return statistics.median(values) if values else 0.0

    @staticmethod
    def mode(values: list[float]) -> list[float]:
        """The most frequent value(s). Returns a list (may be multi-modal)."""
        if not values:
            return []
        try:
            result = statistics.multimode(values)
        except TypeError:
            result = [max(set(values), key=values.count)]
        return result

    @staticmethod
    def quantile(values: list[float], q: float) -> float:
        """Linear-interpolation quantile; ``q`` must be in [0, 1]."""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        position = q * (len(sorted_values) - 1)
        lower = int(position)
        upper = min(lower + 1, len(sorted_values) - 1)
        fraction = position - lower
        return round(
            sorted_values[lower] * (1 - fraction) + sorted_values[upper] * fraction,
            4,
        )

    # -- dispersion ----------------------------------------------------------

    @staticmethod
    def stdev(values: list[float]) -> float:
        return statistics.pstdev(values) if len(values) > 1 else 0.0

    @staticmethod
    def variance(values: list[float]) -> float:
        return statistics.pvariance(values) if len(values) > 1 else 0.0

    def range(self, values: list[float]) -> float:
        return max(values) - min(values) if values else 0.0

    def iqr(self, values: list[float]) -> float:
        """Interquartile range (Q3 − Q1)."""
        if not values:
            return 0.0
        return round(self.quantile(values, 0.75) - self.quantile(values, 0.25), 4)

    # -- shape ---------------------------------------------------------------

    def skewness(self, values: list[float]) -> float:
        """Sample skewness (0 = symmetric, >0 = right tail)."""
        if len(values) < 3:
            return 0.0
        mean = statistics.mean(values)
        stdev = statistics.pstdev(values)
        if stdev == 0:
            return 0.0
        n = len(values)
        skew = sum((v - mean) ** 3 for v in values) / n / (stdev ** 3)
        return round(skew, 4)

    def kurtosis(self, values: list[float]) -> float:
        """Excess kurtosis (0 = normal distribution)."""
        if len(values) < 4:
            return 0.0
        mean = statistics.mean(values)
        stdev = statistics.pstdev(values)
        if stdev == 0:
            return 0.0
        n = len(values)
        kurt = sum((v - mean) ** 4 for v in values) / n / (stdev ** 4) - 3
        return round(kurt, 4)

    # -- frequency -----------------------------------------------------------

    def frequency(self, values: list[float], bins: int = 10) -> dict[str, Any]:
        """Numeric histogram with inclusive last bin (max value never dropped)."""
        numeric = [v for v in values if isinstance(v, (int, float)) and not isinstance(v, bool)]
        if not numeric:
            return {"kind": "empty", "bins": [], "count": 0}
        low, high = min(numeric), max(numeric)
        if low == high:
            return {
                "kind": "numeric",
                "bins": [{"range": [low, high], "count": len(numeric)}],
                "count": len(numeric),
            }
        width = (high - low) / bins
        histogram: list[dict[str, Any]] = []
        for i in range(bins):
            lower = low + i * width
            upper = low + (i + 1) * width
            if i == bins - 1:
                count = sum(1 for v in numeric if lower <= v <= upper)
            else:
                count = sum(1 for v in numeric if lower <= v < upper)
            histogram.append({"range": [round(lower, 4), round(upper, 4)], "count": count})
        return {"kind": "numeric", "bins": histogram, "count": len(numeric)}

    # -- record helpers ------------------------------------------------------

    @staticmethod
    def extract(records: list[DataRecord], field: str) -> list[float]:
        """Pull numeric values for a field out of a list of records."""
        return [
            r.data[field] for r in records
            if isinstance(r.data.get(field), (int, float))
            and not isinstance(r.data.get(field), bool)
        ]

    def describe_records(self, records: list[DataRecord], field: str) -> dict[str, Any]:
        """Full descriptive summary for a field across records."""
        return self.summarize(self.extract(records, field), name=field)

    # -- high-level ----------------------------------------------------------

    def summarize(self, values: list[float], name: str = "value") -> dict[str, Any]:
        """Run the full descriptive toolkit and cache the result by name."""
        result: dict[str, Any] = {
            "name": name,
            "count": len(values),
            "mean": round(self.mean(values), 4),
            "median": round(self.median(values), 4),
            "mode": [round(v, 4) for v in self.mode(values)],
            "min": round(min(values), 4) if values else 0.0,
            "max": round(max(values), 4) if values else 0.0,
            "range": round(self.range(values), 4),
            "stdev": round(self.stdev(values), 4),
            "variance": round(self.variance(values), 4),
            "q1": self.quantile(values, 0.25),
            "q3": self.quantile(values, 0.75),
            "iqr": self.iqr(values),
            "skewness": self.skewness(values),
            "kurtosis": self.kurtosis(values),
            "sum": round(sum(values), 4),
        }
        summary_id = f"desc_{len(self._summaries) + 1}"
        self._summaries[summary_id] = result
        if self.engine is not None:
            self.engine.metrics.increment("analytics.descriptive_runs", labels={"field": name})
        return result

    def history(self) -> dict[str, dict[str, Any]]:
        return dict(self._summaries)


__all__ = ["DescriptiveAnalyzer"]
