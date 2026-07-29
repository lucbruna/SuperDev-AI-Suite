"""
Legal Metrics - KPI calculations and performance metrics for Legal.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from .legal_context import LegalContext

logger = logging.getLogger(__name__)


class MetricCategory(Enum):
    CONTRACTS = "contracts"
    COMPLIANCE = "compliance"
    RISK = "risk"
    AUDIT = "audit"
    POLICIES = "policies"
    LITIGATION = "litigation"


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


class LegalMetrics:
    def __init__(self, context: LegalContext):
        self.context = context
        self._definitions: Dict[str, MetricDefinition] = {}
        self._history: Dict[str, List[MetricValue]] = {}
        self._max_history = 365
        self._calc_functions: Dict[str, Callable] = {}
        self._init_definitions()

    def _init_definitions(self) -> None:
        defs = [
            MetricDefinition("contracts_reviewed", "Contracts Reviewed", "Total contracts analyzed", MetricCategory.CONTRACTS, "count", True),
            MetricDefinition("avg_review_time", "Avg Review Time", "Average contract review hours", MetricCategory.CONTRACTS, "hours", False, 24.0, 48.0),
            MetricDefinition("risk_clause_rate", "Risk Clause Rate", "Percent of contracts with risk clauses", MetricCategory.CONTRACTS, "%", False, 15.0, 30.0),
            MetricDefinition("contract_cycle_time", "Contract Cycle Time", "Days to complete contract", MetricCategory.CONTRACTS, "days", False, 14.0, 21.0),

            MetricDefinition("compliance_score", "Compliance Score", "Overall compliance rating", MetricCategory.COMPLIANCE, "score", True, 90.0, 75.0),
            MetricDefinition("violations_found", "Violations Found", "Active compliance violations", MetricCategory.COMPLIANCE, "count", False, 0.0, 5.0),
            MetricDefinition("control_effectiveness", "Control Effectiveness", "Percent of controls passing", MetricCategory.COMPLIANCE, "%", True, 95.0, 80.0),
            MetricDefinition("regulation_coverage", "Regulation Coverage", "Percent of regulations monitored", MetricCategory.COMPLIANCE, "%", True, 90.0, 70.0),

            MetricDefinition("risk_score", "Risk Score", "Overall legal risk score", MetricCategory.RISK, "score", False, 20.0, 40.0),
            MetricDefinition("high_risk_items", "High Risk Items", "Number of high-risk findings", MetricCategory.RISK, "count", False, 0.0, 5.0),
            MetricDefinition("mitigation_rate", "Mitigation Rate", "Percent of risks mitigated", MetricCategory.RISK, "%", True, 80.0, 60.0),
            MetricDefinition("exposure_value", "Exposure Value", "Total financial exposure", MetricCategory.RISK, "$", False),

            MetricDefinition("audits_completed", "Audits Completed", "Audits this period", MetricCategory.AUDIT, "count", True),
            MetricDefinition("findings_resolved", "Findings Resolved", "Percent of findings closed", MetricCategory.AUDIT, "%", True, 85.0, 65.0),
            MetricDefinition("audit_coverage", "Audit Coverage", "Percent of areas audited", MetricCategory.AUDIT, "%", True, 80.0, 60.0),

            MetricDefinition("policies_active", "Active Policies", "Number of active policies", MetricCategory.POLICIES, "count", True),
            MetricDefinition("acknowledgment_rate", "Acknowledgment Rate", "Percent of employees acknowledged", MetricCategory.POLICIES, "%", True, 95.0, 80.0),

            MetricDefinition("active_cases", "Active Cases", "Active litigation cases", MetricCategory.LITIGATION, "count", False),
            MetricDefinition("deadline_compliance", "Deadline Compliance", "Percent of deadlines met", MetricCategory.LITIGATION, "%", True, 95.0, 80.0),
            MetricDefinition("case_win_rate", "Case Win Rate", "Percent of cases won", MetricCategory.LITIGATION, "%", True, 70.0, 50.0),
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
    def __init__(self, context: LegalContext):
        self.metrics = LegalMetrics(context)
        self.context = context

    async def calculate_all(self) -> Dict[str, float]:
        kpis = {
            "contracts_reviewed": 45.0, "avg_review_time": 18.0, "risk_clause_rate": 12.0, "contract_cycle_time": 10.0,
            "compliance_score": 92.0, "violations_found": 2.0, "control_effectiveness": 96.0, "regulation_coverage": 88.0,
            "risk_score": 18.0, "high_risk_items": 1.0, "mitigation_rate": 85.0, "exposure_value": 250000.0,
            "audits_completed": 8.0, "findings_resolved": 88.0, "audit_coverage": 82.0,
            "policies_active": 25.0, "acknowledgment_rate": 96.0,
            "active_cases": 5.0, "deadline_compliance": 97.0, "case_win_rate": 75.0,
        }
        for k, v in kpis.items():
            self.metrics.record_value(k, v)
        return kpis

    async def get_contract_kpis(self) -> Dict[str, float]:
        return {k: v for k, v in (await self.calculate_all()).items()
                if k in ("contracts_reviewed", "avg_review_time", "risk_clause_rate", "contract_cycle_time")}

    async def get_compliance_kpis(self) -> Dict[str, float]:
        return {k: v for k, v in (await self.calculate_all()).items()
                if k in ("compliance_score", "violations_found", "control_effectiveness", "regulation_coverage")}

    async def get_risk_kpis(self) -> Dict[str, float]:
        return {k: v for k, v in (await self.calculate_all()).items()
                if k in ("risk_score", "high_risk_items", "mitigation_rate", "exposure_value")}
