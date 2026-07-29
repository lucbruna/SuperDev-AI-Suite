from __future__ import annotations

import uuid
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Optional

THRESHOLD_RULES: list[dict[str, Any]] = [
    {"metric": "temperature", "min": -20.0, "max": 60.0, "unit": "celsius"},
    {"metric": "humidity", "min": 0.0, "max": 100.0, "unit": "percent"},
    {"metric": "pressure", "min": 800.0, "max": 1200.0, "unit": "hPa"},
    {"metric": "vibration", "min": 0.0, "max": 50.0, "unit": "mm/s"},
    {"metric": "voltage", "min": 0.0, "max": 240.0, "unit": "V"},
]


class TelemetryProcessor:
    def __init__(self) -> None:
        self._readings: list[dict[str, Any]] = []
        self._aggregated: dict[str, dict[str, float]] = defaultdict(
            lambda: {"sum": 0.0, "count": 0, "min": float("inf"), "max": float("-inf")}
        )
        self.threshold_rules = THRESHOLD_RULES

    async def process_reading(self, reading: dict[str, Any]) -> dict[str, Any]:
        processed = dict(reading)
        processed["processed_at"] = datetime.utcnow().isoformat()
        processed["reading_id"] = reading.get("id", uuid.uuid4().hex)
        self._readings.append(processed)
        self._update_aggregation(processed)
        threshold_check = await self.detect_threshold_breach(processed)
        processed["threshold_breach"] = threshold_check
        return processed

    async def aggregate_data(self, metric: Optional[str] = None, window_minutes: int = 60) -> dict[str, Any]:
        cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)
        filtered = [
            r for r in self._readings
            if (metric is None or r.get("metric") == metric)
            and self._parse_ts(r) >= cutoff
        ]
        if not filtered:
            return {"metric": metric, "window": window_minutes, "count": 0}
        values = [r.get("value", 0) for r in filtered]
        return {
            "metric": metric or "all",
            "window_minutes": window_minutes,
            "count": len(values),
            "sum": sum(values),
            "avg": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
        }

    async def calculate_statistics(self, readings: list[dict[str, Any]]) -> dict[str, float]:
        values = [r.get("value", 0) for r in readings if r.get("value") is not None]
        if not values:
            return {"count": 0, "sum": 0.0, "mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0}
        n = len(values)
        mean = sum(values) / n
        variance = sum((v - mean) ** 2 for v in values) / n
        return {
            "count": n,
            "sum": sum(values),
            "mean": mean,
            "std": variance ** 0.5,
            "min": min(values),
            "max": max(values),
        }

    async def get_timeseries(self, device_id: str, metric: Optional[str] = None, limit: int = 50) -> list[dict[str, Any]]:
        filtered = [
            r for r in self._readings
            if r.get("device_id") == device_id
            and (metric is None or r.get("metric") == metric)
        ]
        return filtered[-limit:]

    async def detect_threshold_breach(self, reading: dict[str, Any]) -> dict[str, Any]:
        metric = reading.get("metric", reading.get("type", ""))
        value = reading.get("value")
        if value is None:
            return {"breach": False, "message": "No value provided"}
        for rule in self.threshold_rules:
            if rule["metric"] == metric:
                if value < rule["min"] or value > rule["max"]:
                    return {
                        "breach": True,
                        "metric": metric,
                        "value": value,
                        "min": rule["min"],
                        "max": rule["max"],
                        "message": f"{metric} value {value} is outside range [{rule['min']}, {rule['max']}]",
                    }
        return {"breach": False, "message": "Within acceptable range"}

    def _update_aggregation(self, reading: dict[str, Any]) -> None:
        metric = reading.get("metric", reading.get("type", "unknown"))
        value = reading.get("value")
        if value is None:
            return
        agg = self._aggregated[metric]
        agg["sum"] += value
        agg["count"] += 1
        agg["min"] = min(agg["min"], value)
        agg["max"] = max(agg["max"], value)

    @staticmethod
    def _parse_ts(reading: dict[str, Any]) -> datetime:
        ts = reading.get("timestamp", reading.get("processed_at", ""))
        if isinstance(ts, datetime):
            return ts
        try:
            return datetime.fromisoformat(ts.replace("Z", "+00:00").split("+")[0])
        except (ValueError, AttributeError):
            return datetime.min
