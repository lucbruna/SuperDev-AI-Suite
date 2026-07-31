"""Analytics engine (attached by the facade as ``analytics``).

Routes metric names to the descriptive / diagnostic / predictive /
prescriptive providers and exposes each level directly.
"""

from __future__ import annotations

from typing import Any

from data_intelligence.analytics.base import AnalyticsError, AnalyticsProvider
from data_intelligence.analytics.descriptive import DescriptiveAnalytics
from data_intelligence.analytics.diagnostic import DiagnosticAnalytics
from data_intelligence.analytics.metrics import (average, growth_rate,
                                                 percentage, total)
from data_intelligence.analytics.predictive import PredictiveAnalytics
from data_intelligence.analytics.prescriptive import PrescriptiveAnalytics
from data_intelligence.data_events import DataIntelligenceEvents
from data_intelligence.data_logger import get_logger
from data_intelligence.data_metrics import DataIntelligenceMetrics
from data_intelligence.data_models import AnalyticsLevel, AnalyticsResult


class AnalyticsEngine:
    """Coordinates the four analytics levels."""

    LEVELS = {
        AnalyticsLevel.DESCRIPTIVE: "descriptive",
        AnalyticsLevel.DIAGNOSTIC: "diagnostic",
        AnalyticsLevel.PREDICTIVE: "predictive",
        AnalyticsLevel.PRESCRIPTIVE: "prescriptive",
    }

    def __init__(self, events: DataIntelligenceEvents,
                 metrics: DataIntelligenceMetrics, config: Any,
                 context: Any,
                 descriptive: AnalyticsProvider | None = None,
                 diagnostic: AnalyticsProvider | None = None,
                 predictive: AnalyticsProvider | None = None,
                 prescriptive: AnalyticsProvider | None = None) -> None:
        self._log = get_logger()
        self.events = events
        self.metrics = metrics
        self.config = config
        self.context = context
        self.descriptive = descriptive or DescriptiveAnalytics()
        self.diagnostic = diagnostic or DiagnosticAnalytics()
        self.predictive = predictive or PredictiveAnalytics()
        self.prescriptive = prescriptive or PrescriptiveAnalytics()
        self.history: list[dict[str, Any]] = []

    # -- routing -----------------------------------------------------------
    def provider_for(self, metric: str) -> tuple[AnalyticsProvider, str]:
        key = metric.lower()
        if key in ("total", "average", "growth", "distribution"):
            return self.descriptive, "descriptive"
        if key in ("compare", "anomalies", "why", "cause"):
            return self.diagnostic, "diagnostic"
        if key in ("trend", "days_until", "run_rate", "forecast",
                   "predict"):
            return self.predictive, "predictive"
        if key in ("recommend", "gap_to_target", "action"):
            return self.prescriptive, "prescriptive"
        return self.descriptive, "descriptive"

    def compute(self, metric: str,
                data: list[dict[str, Any]]) -> dict[str, Any]:
        """Computes the metric (AnalyticsProvider-compatible)."""
        provider, level_name = self.provider_for(metric)
        with self.metrics.timed(f"analytics.{level_name}"):
            result = provider.compute(metric, data)
        result["level"] = level_name
        self.history.append(result)
        return result

    # -- level helpers -----------------------------------------------------
    def descriptive_result(self, metric: str,
                           data: list[dict[str, Any]]) -> AnalyticsResult:
        raw = self.compute(metric, data)
        return AnalyticsResult(level=AnalyticsLevel.DESCRIPTIVE,
                               metric=metric, value=raw.get("value"),
                               detail=raw.get("detail", {}))

    def run_analysis(self, level: AnalyticsLevel, metric: str,
                     data: list[dict[str, Any]]) -> AnalyticsResult:
        """Runs a metric at an explicit level and returns an AnalyticsResult."""
        provider = getattr(self, self.LEVELS[level])
        raw = provider.compute(metric, data)
        return AnalyticsResult(level=level, metric=metric,
                               value=raw.get("value"),
                               detail=raw.get("detail", {}))

    def stats(self) -> dict[str, Any]:
        return {"computations": len(self.history),
                "levels": {name: {
                    "computations": len([h for h in self.history
                                         if h.get("level") == name])}
                    for name in self.LEVELS.values()}}


__all__ = ["AnalyticsEngine", "AnalyticsProvider", "AnalyticsError",
           "DescriptiveAnalytics", "DiagnosticAnalytics",
           "PredictiveAnalytics", "PrescriptiveAnalytics",
           "total", "average", "growth_rate", "percentage"]
