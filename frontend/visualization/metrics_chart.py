from __future__ import annotations

from typing import Any


class MetricsChart:
    """Builds chart data for metrics visualization."""

    KINDS = ("line", "bar", "pie", "area", "scatter")

    def __init__(self) -> None:
        self._charts: list[dict[str, Any]] = []

    def line(self, name: str, series: list[dict[str, Any]], **props: Any) -> dict[str, Any]:
        return self._make(name, "line", series, **props)

    def bar(self, name: str, series: list[dict[str, Any]], **props: Any) -> dict[str, Any]:
        return self._make(name, "bar", series, **props)

    def pie(self, name: str, values: list[dict[str, Any]], **props: Any) -> dict[str, Any]:
        return self._make(name, "pie", values, **props)

    def _make(self, name: str, kind: str, data: list[Any], **props: Any) -> dict[str, Any]:
        if kind not in self.KINDS:
            raise ValueError(f"unsupported chart kind: {kind}")
        chart = {"name": name, "kind": kind, "data": data, "props": props}
        self._charts.append(chart)
        return chart

    def list(self) -> list[dict[str, Any]]:
        return list(self._charts)

    def aggregate(self, series: list[dict[str, Any]], field: str = "value") -> dict[str, float]:
        values = [float(item.get(field, 0)) for item in series]
        if not values:
            return {"min": 0.0, "max": 0.0, "avg": 0.0, "sum": 0.0}
        return {
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "sum": sum(values),
        }
