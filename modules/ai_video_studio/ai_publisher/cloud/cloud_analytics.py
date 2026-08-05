"""Cloud Analytics — usage and transfer statistics (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class CloudAnalytics:
    """Track cloud usage, transfers, and cost metrics."""

    def __init__(self) -> None:
        self._events: list[dict] = []

    def ingest(self, *, event: dict) -> dict:
        """Record a usage event (downloads, uploads, egress)."""
        self._events.append(dict(event))
        return {"ingested": 1, "total": len(self._events)}

    def summary(self) -> dict:
        keys = ["downloads", "uploads", "egress_gb", "storage_gb"]
        totals: dict[str, float] = {k: 0.0 for k in keys}
        for event in self._events:
            for key in keys:
                totals[key] += event.get(key, 0) or 0
        totals["estimated_cost_usd"] = round(totals["storage_gb"] * 0.023 + totals["egress_gb"] * 0.09, 2)
        return totals

    def stats(self) -> dict[str, int]:
        return {"events": len(self._events)}


_ANALYTICS: CloudAnalytics | None = None


def get_cloud_analytics() -> CloudAnalytics:
    """Get the module-level singleton cloud analytics."""
    global _ANALYTICS
    if _ANALYTICS is None:
        _ANALYTICS = CloudAnalytics()
    return _ANALYTICS
