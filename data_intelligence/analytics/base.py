"""Base classes for analytics providers."""

from __future__ import annotations

from typing import Any

from data_intelligence.data_models import AnalyticsLevel


class AnalyticsError(Exception):
    """Raised when an analytics computation fails."""


class AnalyticsProvider:
    """Base class for an analytics level provider."""

    level = AnalyticsLevel.DESCRIPTIVE

    def compute(self, metric: str,
                data: list[dict[str, Any]]) -> dict[str, Any]:
        """Computes the metric over the given records."""
        raise NotImplementedError
