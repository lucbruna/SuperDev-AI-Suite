"""Pattern analysis."""

from __future__ import annotations


class PatternAnalyzer:
    def __init__(self) -> None:
        self._patterns: dict[str, list[float]] = {}

    def record(self, metric_name: str, value: float) -> None:
        self._patterns.setdefault(metric_name, []).append(value)
        if len(self._patterns[metric_name]) > 1000:
            self._patterns[metric_name] = self._patterns[metric_name][-1000:]

    def detect_trend(self, metric_name: str) -> str:
        values = self._patterns.get(metric_name, [])
        if len(values) < 5:
            return "insufficient_data"
        recent = values[-5:]
        if all(recent[i] <= recent[i + 1] for i in range(len(recent) - 1)):
            return "increasing"
        if all(recent[i] >= recent[i + 1] for i in range(len(recent) - 1)):
            return "decreasing"
        return "fluctuating"

    def detect_periodicity(self, metric_name: str, period: int = 24) -> bool:
        values = self._patterns.get(metric_name, [])
        if len(values) < period * 2:
            return False
        correlations = []
        for i in range(len(values) - period):
            correlations.append(values[i] * values[i + period])
        avg_corr = sum(correlations) / len(correlations) if correlations else 0
        return avg_corr > 0

    def list_metrics(self) -> list[str]:
        return list(self._patterns.keys())

    def get_values(self, metric_name: str) -> list[float]:
        return list(self._patterns.get(metric_name, []))
