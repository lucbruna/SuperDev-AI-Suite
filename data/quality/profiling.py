from __future__ import annotations

import statistics
from typing import Any

from ..data_models import DataRecord


class DataProfiler:
    """Data profiling toolkit.

    Analyzes datasets of :class:`DataRecord` and produces per-field profiles:
    inferred types, null rates, cardinality, numeric statistics, value
    distributions and cross-dataset drift — the input signal for the
    QualityEngine.
    """

    def __init__(self, engine: Any | None = None) -> None:
        self.engine = engine
        self._profiles: dict[str, dict[str, Any]] = {}

    # -- type inference ------------------------------------------------------

    @staticmethod
    def infer_type(values: list[Any]) -> str:
        """Infer the dominant data type of a list of values."""
        non_null = [v for v in values if v is not None and v != ""]
        if not non_null:
            return "empty"
        if all(isinstance(v, bool) for v in non_null):
            return "boolean"
        if all(isinstance(v, (int, float)) for v in non_null):
            return "numeric"
        if all(isinstance(v, str) for v in non_null):
            return "text"
        return "mixed"

    # -- field profile -------------------------------------------------------

    def profile_field(self, records: list[DataRecord], field: str) -> dict[str, Any]:
        """Profile a single field across all records."""
        values = [r.data.get(field) for r in records]
        non_null = [v for v in values if v is not None and v != ""]
        total = len(values)
        nulls = total - len(non_null)

        profile: dict[str, Any] = {
            "field": field,
            "type": self.infer_type(values),
            "count": total,
            "nulls": nulls,
            "null_rate": round(nulls / total, 4) if total else 0.0,
            "unique": len({repr(v) for v in non_null}),
        }

        numeric = [v for v in non_null if isinstance(v, (int, float)) and not isinstance(v, bool)]
        if numeric:
            profile.update({
                "min": round(min(numeric), 4),
                "max": round(max(numeric), 4),
                "mean": round(statistics.mean(numeric), 4),
                "median": round(statistics.median(numeric), 4),
                "stdev": round(statistics.pstdev(numeric), 4),
            })
        else:
            profile["top_values"] = self._top_values(non_null, limit=5)
        return profile

    @staticmethod
    def _top_values(values: list[Any], limit: int = 5) -> list[dict[str, Any]]:
        counts: dict[Any, int] = {}
        for value in values:
            counts[value] = counts.get(value, 0) + 1
        ranked = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:limit]
        return [{"value": value, "count": count} for value, count in ranked]

    # -- dataset profile -----------------------------------------------------

    def profile(self, records: list[DataRecord], asset_id: str = "") -> dict[str, Any]:
        """Profile an entire dataset and cache the result by asset id."""
        if not records:
            report: dict[str, Any] = {
                "asset_id": asset_id or "default",
                "records": 0,
                "fields": [],
                "duplicate_rate": 0.0,
                "overall_null_rate": 0.0,
            }
            self._profiles[report["asset_id"]] = report
            return report

        fields = sorted({key for r in records for key in r.data})
        field_profiles = {field: self.profile_field(records, field) for field in fields}

        seen: set[str] = set()
        duplicates = 0
        total_null = 0
        total_cells = 0
        for record in records:
            key = repr(sorted(record.data.items()))
            if key in seen:
                duplicates += 1
            seen.add(key)
            total_null += sum(1 for v in record.data.values() if v is None or v == "")
            total_cells += len(record.data)

        report = {
            "asset_id": asset_id or "default",
            "records": len(records),
            "fields": field_profiles,
            "duplicate_rate": round(duplicates / len(records), 4),
            "overall_null_rate": round(total_null / max(total_cells, 1), 4),
        }
        self._profiles[report["asset_id"]] = report
        if self.engine is not None:
            self.engine.metrics.increment("quality.profiling_runs", labels={"asset": asset_id})
        return report

    def get_profile(self, asset_id: str) -> dict[str, Any] | None:
        return self._profiles.get(asset_id)

    # -- distributions -------------------------------------------------------

    def distribution(
        self,
        records: list[DataRecord],
        field: str,
        bins: int = 10,
    ) -> dict[str, Any]:
        """Numeric histogram or categorical frequency distribution for a field."""
        values = [
            r.data.get(field) for r in records
            if isinstance(r.data.get(field), (int, float))
            and not isinstance(r.data.get(field), bool)
        ]
        if not values:
            non_numeric = [
                r.data.get(field) for r in records
                if r.data.get(field) is not None and r.data.get(field) != ""
            ]
            return {
                "field": field,
                "kind": "categorical",
                "top_values": self._top_values(non_numeric, limit=bins),
            }

        low, high = min(values), max(values)
        if low == high:
            return {"field": field, "kind": "numeric", "bins": [{"range": [low, high], "count": len(values)}]}

        width = (high - low) / bins
        histogram: list[dict[str, Any]] = []
        for i in range(bins):
            lower = low + i * width
            upper = low + (i + 1) * width
            # Last bin is inclusive so the maximum value is never dropped.
            if i == bins - 1:
                count = sum(1 for v in values if lower <= v <= upper)
            else:
                count = sum(1 for v in values if lower <= v < upper)
            histogram.append({"range": [round(lower, 4), round(upper, 4)], "count": count})
        return {"field": field, "kind": "numeric", "bins": histogram}

    # -- drift ---------------------------------------------------------------

    def drift_score(
        self,
        baseline: dict[str, Any],
        current: dict[str, Any],
    ) -> float:
        """Population drift between two profiles (0.0 identical → 1.0 different).

        Compares numeric means and categorical top-value overlap across
        shared fields.
        """
        base_fields = baseline.get("fields", {})
        curr_fields = current.get("fields", {})
        scores: list[float] = []

        for field in set(base_fields) & set(curr_fields):
            base = base_fields[field]
            curr = curr_fields[field]
            if base.get("type") == "numeric" and curr.get("type") == "numeric":
                base_mean = base.get("mean", 0.0)
                curr_mean = curr.get("mean", 0.0)
                spread = max(abs(base_mean), abs(curr_mean), 1e-9)
                scores.append(min(1.0, abs(base_mean - curr_mean) / spread))
            elif base.get("type") == curr.get("type"):
                base_top = {t["value"] for t in base.get("top_values", [])}
                curr_top = {t["value"] for t in curr.get("top_values", [])}
                union = base_top | curr_top
                if union:
                    scores.append(1 - len(base_top & curr_top) / len(union))

        return round(statistics.mean(scores), 4) if scores else 0.0


__all__ = ["DataProfiler"]
