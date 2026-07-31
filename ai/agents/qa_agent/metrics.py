from __future__ import annotations

from typing import Any


class Metrics:
    """Tracks and reports quality metrics over time."""

    def __init__(self) -> None:
        self._data: dict[str, list[dict[str, Any]]] = {}

    def record(self, name: str, value: float, tags: dict[str, Any] | None = None) -> str:
        if name not in self._data:
            self._data[name] = []
        self._data[name].append(
            {
                "value": value,
                "tags": tags or {},
            }
        )
        return name

    def get_metric(self, name: str) -> list[dict[str, Any]]:
        return list(self._data.get(name, []))

    def list_metric_names(self) -> list[str]:
        return list(self._data.keys())

    @property
    def metric_count(self) -> int:
        return len(self._data)

    def summary(self, name: str) -> dict[str, Any]:
        points = self._data.get(name, [])
        if not points:
            return {"name": name, "count": 0}
        values = [p["value"] for p in points]
        return {
            "name": name,
            "count": len(values),
            "min": round(min(values), 2),
            "max": round(max(values), 2),
            "avg": round(sum(values) / len(values), 2),
            "last": values[-1],
        }

    def generate_dashboard(self) -> str:
        if not self._data:
            return "+----------------------+\n|  No metrics recorded  |\n+----------------------+"
        lines = ["+----------------------+", "|   Metrics Dashboard   |", "+----------------------+"]
        for name in sorted(self._data.keys()):
            s = self.summary(name)
            lines.append(f"  {name}:")
            lines.append(f"    Count: {s['count']}  |  Avg: {s['avg']}  |  Last: {s['last']}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        return {
            "metrics": {k: v for k, v in self._data.items()},
            "metric_count": self.metric_count,
        }
