"""Analytics subsystem (Volume 22).

Four analytics levels: descriptive (what happened), diagnostic (why),
predictive (what will happen) and prescriptive (what to do).
"""

from __future__ import annotations

from data_intelligence.analytics.base import AnalyticsError, AnalyticsProvider
from data_intelligence.analytics.descriptive import DescriptiveAnalytics
from data_intelligence.analytics.diagnostic import DiagnosticAnalytics
from data_intelligence.analytics.engine import AnalyticsEngine
from data_intelligence.analytics.metrics import (average, growth_rate,
                                                 percentage, total)
from data_intelligence.analytics.predictive import PredictiveAnalytics
from data_intelligence.analytics.prescriptive import PrescriptiveAnalytics

__all__ = [
    "AnalyticsEngine", "AnalyticsProvider", "AnalyticsError",
    "DescriptiveAnalytics", "DiagnosticAnalytics", "PredictiveAnalytics",
    "PrescriptiveAnalytics", "total", "average", "growth_rate", "percentage",
]
