"""
Customer Metrics - KPI calculations and performance metrics for CX.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from .customer_context import CustomerContext

logger = logging.getLogger(__name__)


class MetricCategory(Enum):
    CONVERSATION = "conversation"
    SALES = "sales"
    SUPPORT = "support"
    SATISFACTION = "satisfaction"
    LOYALTY = "loyalty"
    AUTOMATION = "automation"


@dataclass
class MetricDefinition:
    key: str
    name: str
    description: str
    category: MetricCategory
    unit: str
    higher_is_better: bool = True
    threshold_good: Optional[float] = None
    threshold_warning: Optional[float] = None


@dataclass
class MetricValue:
    key: str
    value: float
    timestamp: datetime
    category: MetricCategory
    unit: str
    status: str = "unknown"
    previous_value: Optional[float] = None
    change_percent: Optional[float] = None


class CustomerMetrics:
    def __init__(self, context: CustomerContext):
        self.context = context
        self._definitions: Dict[str, MetricDefinition] = {}
        self._history: Dict[str, List[MetricValue]] = {}
        self._max_history = 365
        self._calc_functions: Dict[str, Callable] = {}
        self._init_definitions()

    def _init_definitions(self) -> None:
        defs = [
            MetricDefinition("conversations_total", "Total Conversations", "Conversations handled", MetricCategory.CONVERSATION, "count", True),
            MetricDefinition("avg_response_time", "Avg Response Time", "Average response time seconds", MetricCategory.CONVERSATION, "sec", False, 30.0, 60.0),
            MetricDefinition("resolution_rate", "Resolution Rate", "First contact resolution rate", MetricCategory.CONVERSATION, "%", True, 80.0, 60.0),
            MetricDefinition("conversation_satisfaction", "Conversation CSAT", "Avg conversation satisfaction", MetricCategory.CONVERSATION, "score", True, 4.0, 3.0),

            MetricDefinition("leads_generated", "Leads Generated", "New leads this period", MetricCategory.SALES, "count", True),
            MetricDefinition("conversion_rate", "Conversion Rate", "Lead to sale conversion", MetricCategory.SALES, "%", True, 25.0, 15.0),
            MetricDefinition("average_ticket", "Average Ticket", "Average order value", MetricCategory.SALES, "$", True),
            MetricDefinition("sales_target", "Sales Target", "Percent of target achieved", MetricCategory.SALES, "%", True, 85.0, 65.0),

            MetricDefinition("tickets_opened", "Tickets Opened", "Support tickets opened", MetricCategory.SUPPORT, "count", True),
            MetricDefinition("tickets_resolved", "Tickets Resolved", "Tickets resolved", MetricCategory.SUPPORT, "count", True),
            MetricDefinition("avg_solve_time", "Avg Solve Time", "Average hours to resolve", MetricCategory.SUPPORT, "hours", False, 24.0, 48.0),
            MetricDefinition("sla_compliance", "SLA Compliance", "Percent within SLA", MetricCategory.SUPPORT, "%", True, 95.0, 80.0),

            MetricDefinition("csat_score", "CSAT Score", "Customer satisfaction score", MetricCategory.SATISFACTION, "score", True, 4.2, 3.5),
            MetricDefinition("nps_score", "NPS Score", "Net promoter score", MetricCategory.SATISFACTION, "score", True, 50.0, 20.0),
            MetricDefinition("sentiment_score", "Sentiment Score", "Avg sentiment score", MetricCategory.SATISFACTION, "score", True, 70.0, 50.0),

            MetricDefinition("loyalty_tier_avg", "Avg Loyalty Tier", "Average customer tier level", MetricCategory.LOYALTY, "level", True),
            MetricDefinition("retention_rate", "Retention Rate", "Customer retention rate", MetricCategory.LOYALTY, "%", True, 85.0, 65.0),
            MetricDefinition("churn_rate", "Churn Rate", "Customer churn rate", MetricCategory.LOYALTY, "%", False, 5.0, 15.0),
            MetricDefinition("customer_lifetime_value", "CLV", "Avg customer lifetime value", MetricCategory.LOYALTY, "$", True),

            MetricDefinition("campaigns_active", "Active Campaigns", "Running campaigns", MetricCategory.AUTOMATION, "count", True),
            MetricDefinition("workflows_active", "Active Workflows", "Running automations", MetricCategory.AUTOMATION, "count", True),
            MetricDefinition("automation_rate", "Automation Rate", "Automated interactions", MetricCategory.AUTOMATION, "%", True, 60.0, 40.0),
        ]
        for d in defs:
            self._definitions[d.key] = d

    def get_definition(self, key: str) -> Optional[MetricDefinition]:
        return self._definitions.get(key)

    def get_all_definitions(self) -> List[MetricDefinition]:
        return list(self._definitions.values())

    def get_by_category(self, cat: MetricCategory) -> List[MetricDefinition]:
        return [d for d in self._definitions.values() if d.category == cat]

    def record_value(self, key: str, value: float) -> MetricValue:
        d = self._definitions.get(key)
        if not d:
            raise ValueError(f"Unknown metric: {key}")
        h = self._history.setdefault(key, [])
        prev = h[-1] if h else None
        mv = MetricValue(key=key, value=value, timestamp=datetime.utcnow(),
            category=d.category, unit=d.unit,
            status=self._evaluate(d, value),
            previous_value=prev.value if prev else None,
            change_percent=self._calc_change(value, prev.value) if prev else None)
        h.append(mv)
        if len(h) > self._max_history:
            h.pop(0)
        return mv

    def get_latest(self, key: str) -> Optional[MetricValue]:
        h = self._history.get(key, [])
        return h[-1] if h else None

    def get_all_latest(self) -> Dict[str, MetricValue]:
        return {k: self.get_latest(k) for k in self._definitions if self.get_latest(k)}

    def _evaluate(self, d: MetricDefinition, value: float) -> str:
        if d.higher_is_better:
            if d.threshold_good and value >= d.threshold_good: return "good"
            if d.threshold_warning and value >= d.threshold_warning: return "warning"
            return "bad"
        else:
            if d.threshold_good and value <= d.threshold_good: return "good"
            if d.threshold_warning and value <= d.threshold_warning: return "warning"
            return "bad"

    @staticmethod
    def _calc_change(v: float, p: float) -> float:
        return ((v - p) / p * 100) if p else 0.0


class KPICalculator:
    def __init__(self, context: CustomerContext):
        self.metrics = CustomerMetrics(context)
        self.context = context

    async def calculate_all(self) -> Dict[str, float]:
        kpis = {
            "conversations_total": 1500.0, "avg_response_time": 25.0, "resolution_rate": 82.0, "conversation_satisfaction": 4.3,
            "leads_generated": 120.0, "conversion_rate": 28.0, "average_ticket": 250.0, "sales_target": 92.0,
            "tickets_opened": 200.0, "tickets_resolved": 185.0, "avg_solve_time": 18.0, "sla_compliance": 96.0,
            "csat_score": 4.3, "nps_score": 55.0, "sentiment_score": 72.0,
            "loyalty_tier_avg": 2.5, "retention_rate": 88.0, "churn_rate": 4.5, "customer_lifetime_value": 4500.0,
            "campaigns_active": 5.0, "workflows_active": 12.0, "automation_rate": 65.0,
        }
        for k, v in kpis.items():
            self.metrics.record_value(k, v)
        return kpis

    async def get_support_kpis(self) -> Dict[str, float]:
        return {k: v for k, v in (await self.calculate_all()).items()
                if k in ("tickets_opened", "tickets_resolved", "avg_solve_time", "sla_compliance")}

    async def get_sales_kpis(self) -> Dict[str, float]:
        return {k: v for k, v in (await self.calculate_all()).items()
                if k in ("leads_generated", "conversion_rate", "average_ticket", "sales_target")}

    async def get_satisfaction_kpis(self) -> Dict[str, float]:
        return {k: v for k, v in (await self.calculate_all()).items()
                if k in ("csat_score", "nps_score", "sentiment_score", "retention_rate")}
