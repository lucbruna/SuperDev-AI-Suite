from __future__ import annotations

import logging
from typing import Any


class AnalyticsOverview:
    """KPIs and trends for the analytics overview."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.analytics.overview")
        self._metrics: dict[str, list[dict[str, Any]]] = {}

    def render(self) -> dict[str, Any]:
        return {"kpis": self.kpis(), "metrics": list(self._metrics)}

    def kpis(self, period: str = "30d") -> dict[str, Any]:
        return {
            "period": period,
            "active_agents": 12,
            "workflows_run": 348,
            "success_rate": 0.97,
            "total_tokens": 1842000,
        }

    def trends(self, metric: str, period: str = "30d") -> list[dict[str, Any]]:
        samples = self._metrics.get(metric, [])
        return [s for s in samples if s.get("period", "30d") == period]
