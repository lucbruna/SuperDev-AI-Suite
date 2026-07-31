from __future__ import annotations

from typing import Any

from ..data_models import DataQualityReport, DataQualityStatus, DataRecord
from .profiling import DataProfiler


class QualityEngine:
    """Data quality — validation, profiling, completeness, accuracy, consistency, monitoring."""

    def __init__(self, engine: Any) -> None:
        self.engine = engine
        self.config = engine.config.quality
        self._reports: dict[str, DataQualityReport] = {}
        self._monitoring: dict[str, list[DataQualityStatus]] = {}
        self._initialized = False
        # Deep-dive toolkit: engine.quality.profiler
        self.profiler = DataProfiler(engine=self.engine)

    async def initialize(self) -> None:
        self._initialized = True

    async def shutdown(self) -> None:
        self._initialized = False

    # -- profiling -----------------------------------------------------------

    def profile(self, records: list[DataRecord], asset_id: str = "") -> DataQualityReport:
        if not records:
            report = DataQualityReport(asset_id=asset_id, completeness=1.0, accuracy=1.0,
                                       consistency=1.0, uniqueness=1.0, validity=1.0)
            self._reports[asset_id or "default"] = report
            return report

        total_fields = sum(len(r.data) for r in records)
        filled_fields = sum(
            1 for r in records
            for v in r.data.values() if v is not None and v != ""
        )
        completeness = filled_fields / max(total_fields, 1)

        numeric = [
            r.data.get("value") for r in records
            if isinstance(r.data.get("value"), (int, float))
        ]
        accuracy = 1.0 if numeric else 0.0

        keys = [str(r.data.get("id", r.id)) for r in records]
        uniqueness = len(set(keys)) / max(len(keys), 1)

        issues: list[dict[str, Any]] = []
        for record in records:
            if record.quality == DataQualityStatus.BAD:
                issues.append({"record_id": record.id, "issue": "bad quality"})

        report = DataQualityReport(
            asset_id=asset_id,
            completeness=round(completeness, 2),
            accuracy=round(accuracy, 2),
            consistency=round(accuracy, 2),
            uniqueness=round(uniqueness, 2),
            validity=round(accuracy, 2),
            issues=issues,
        )
        self._reports[asset_id or "default"] = report
        self.engine.metrics.increment("quality.profiles")
        return report

    def get_report(self, asset_id: str) -> DataQualityReport | None:
        return self._reports.get(asset_id)

    # -- completeness --------------------------------------------------------

    def completeness(self, records: list[DataRecord], field: str) -> float:
        if not records:
            return 1.0
        filled = sum(1 for r in records if r.data.get(field) is not None)
        return round(filled / len(records), 2)

    # -- accuracy ------------------------------------------------------------

    def accuracy(self, records: list[DataRecord], field: str, expected: Any) -> float:
        if not records:
            return 1.0
        matching = sum(1 for r in records if r.data.get(field) == expected)
        return round(matching / len(records), 2)

    # -- consistency ---------------------------------------------------------

    def consistency(self, records: list[DataRecord], field: str) -> float:
        """Fraction of records matching the most common value."""
        if not records:
            return 1.0
        counts: dict[Any, int] = {}
        for r in records:
            value = r.data.get(field)
            counts[value] = counts.get(value, 0) + 1
        most_common = max(counts.values())
        return round(most_common / len(records), 2)

    # -- monitoring ----------------------------------------------------------

    def record_status(self, asset_id: str, status: DataQualityStatus) -> None:
        self._monitoring.setdefault(asset_id, []).append(status)

    def monitor(self, asset_id: str) -> dict[str, Any]:
        statuses = self._monitoring.get(asset_id, [])
        if not statuses:
            return {"asset_id": asset_id, "samples": 0, "status": "no_data"}
        latest = statuses[-1]
        bad = sum(1 for s in statuses if s == DataQualityStatus.BAD)
        return {
            "asset_id": asset_id,
            "samples": len(statuses),
            "status": latest.value,
            "bad_ratio": round(bad / len(statuses), 2),
        }

    def status(self) -> dict[str, Any]:
        return {
            "initialized": self._initialized,
            "reports": len(self._reports),
            "monitored_assets": len(self._monitoring),
        }


__all__ = ["QualityEngine"]
