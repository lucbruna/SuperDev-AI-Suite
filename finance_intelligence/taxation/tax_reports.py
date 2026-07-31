"""Tax reports for the Finance Intelligence Engine (Volume 35)."""

from __future__ import annotations

from typing import Any

from finance_intelligence.finance_models import TaxRecord
from finance_intelligence.finance_protocols import round_money


class TaxReports:
    """Generate summaries from computed tax records."""

    def summary(self, records: list[TaxRecord]) -> dict[str, Any]:
        by_kind: dict[str, float] = {}
        total = 0.0
        for record in records:
            by_kind[record.kind] = round_money(
                by_kind.get(record.kind, 0.0) + record.amount)
            total = round_money(total + record.amount)
        return {"total": total, "by_kind": by_kind,
                "record_count": len(records)}

    def by_period(self, records: list[TaxRecord]) -> dict[str, float]:
        periods: dict[str, float] = {}
        for record in records:
            period = record.period or "unknown"
            periods[period] = round_money(
                periods.get(period, 0.0) + record.amount)
        return periods

    def obligation(self, records: list[TaxRecord],
                   regime: str = "") -> dict[str, Any]:
        summary = self.summary(records)
        return {
            "regime": regime,
            "total_obligation": summary["total"],
            "by_kind": summary["by_kind"],
            "due": summary["total"] > 0,
        }
