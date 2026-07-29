from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..decision_config import DecisionConfig
from ..decision_models import Alert, AlertSeverity, BusinessArea, Insight, InsightType, Pattern
from ..decision_security import DecisionSecurityManager
from .pattern_detector import PatternDetector
from .correlation import CorrelationAnalyzer
from .business_analysis import BusinessAnalysis

logger = logging.getLogger(__name__)


class AnalyticsEngine:
    def __init__(self, config: DecisionConfig, security: DecisionSecurityManager):
        self.config = config
        self.security = security
        self.patterns: Optional[PatternDetector] = None
        self.correlation: Optional[CorrelationAnalyzer] = None
        self.analysis: Optional[BusinessAnalysis] = None
        self._alerts: List[Alert] = []

    async def initialize(self) -> None:
        self.patterns = PatternDetector(self.config)
        self.correlation = CorrelationAnalyzer(self.config)
        self.analysis = BusinessAnalysis(self.config)
        logger.info("AnalyticsEngine initialized")

    async def get_insights(self) -> List[Insight]:
        return self.analysis.generate_insights()

    async def detect_anomalies(self) -> List[Alert]:
        alerts = self.analysis.detect_anomalies()
        self._alerts.extend(alerts)
        return alerts

    async def get_active_alerts(self) -> List[Alert]:
        return [a for a in self._alerts if not a.resolved]

    async def get_patterns(self) -> List[Pattern]:
        return self.patterns.detect()

    async def get_correlations(self) -> List[Dict[str, Any]]:
        return self.correlation.analyze()

    async def run_analysis(self) -> Dict[str, Any]:
        return {
            "insights": len(await self.get_insights()),
            "patterns": len(await self.get_patterns()),
            "correlations": len(await self.get_correlations()),
            "alerts": len(self._alerts),
        }

    async def shutdown(self) -> None:
        logger.info("AnalyticsEngine shutdown")
