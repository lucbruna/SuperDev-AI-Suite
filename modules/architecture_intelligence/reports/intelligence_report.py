"""Aggregate intelligence report for dashboards."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class IntelligenceReport:
    """Composes engine outputs into a single JSON-serializable report."""

    def __init__(self, engine: Any) -> None:
        self.engine = engine

    def build(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "title": "Architecture Intelligence Report",
            "format": "json",
            "source": "architecture_intelligence.reports",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        if not self.engine.available:
            payload["available"] = False
            return payload
        payload["available"] = True
        payload.update(self.engine.report())
        return payload

    def to_dict(self) -> dict[str, Any]:
        return self.build()


def build_report(engine: Any) -> dict[str, Any]:
    return IntelligenceReport(engine).build()
