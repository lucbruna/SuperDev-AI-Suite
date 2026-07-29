from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from .decision_models import (
    ActionPlan, BusinessArea, DecisionLog, DecisionStatus,
    Recommendation, RecommendationPriority, Scenario, ScenarioType,
    SimulationResult,
)

logger = logging.getLogger(__name__)


class StrategyEngine:
    def __init__(self):
        self._decisions: Dict[str, DecisionLog] = {}
        self._action_plans: Dict[str, ActionPlan] = {}

    async def evaluate_strategy(self, scenario: Scenario) -> Dict[str, Any]:
        impact = {}
        for key, value in scenario.parameters.items():
            if isinstance(value, (int, float)):
                impact[f"{key}_impact"] = value * 0.85
            else:
                impact[f"{key}_analysis"] = "Qualitative assessment needed"
        return {
            "scenario_id": scenario.id,
            "feasibility": 0.78,
            "risk_level": "medium",
            "projected_impact": impact,
            "confidence": 0.82,
        }

    async def recommend_strategy(self, context: Dict[str, Any]) -> List[Recommendation]:
        return [
            Recommendation(
                id=str(uuid.uuid4()),
                title="Otimizar estrutura de custos",
                description="Reduzir custos operacionais em 15% através de automação",
                priority=RecommendationPriority.HIGH,
                business_area=BusinessArea.OPERATIONS,
                roi_estimate=250000.0,
                effort_hours=500,
            ),
            Recommendation(
                id=str(uuid.uuid4()),
                title="Expandir mercado digital",
                description="Aumentar presença digital e capturar 20% mais market share",
                priority=RecommendationPriority.MEDIUM,
                business_area=BusinessArea.STRATEGY,
                roi_estimate=800000.0,
                effort_hours=1200,
            ),
        ]

    async def create_action_plan(self, recommendations: List[Recommendation]) -> ActionPlan:
        plan = ActionPlan(
            id=str(uuid.uuid4()),
            title="Strategic Action Plan",
            recommendations=recommendations,
            total_effort_hours=sum(r.effort_hours for r in recommendations),
            total_roi=sum(r.roi_estimate for r in recommendations),
            priority_score=sum(r.roi_estimate for r in recommendations) / max(len(recommendations), 1),
        )
        self._action_plans[plan.id] = plan
        return plan

    async def log_decision(self, decision: str, rationale: str, business_area: BusinessArea = BusinessArea.STRATEGY) -> DecisionLog:
        log = DecisionLog(
            id=str(uuid.uuid4()),
            decision=decision,
            rationale=rationale,
            business_area=business_area,
        )
        self._decisions[log.id] = log
        return log

    async def get_decision_history(self, limit: int = 50) -> List[DecisionLog]:
        sorted_logs = sorted(self._decisions.values(), key=lambda d: d.created_at, reverse=True)
        return sorted_logs[:limit]

    async def get_action_plans(self) -> List[ActionPlan]:
        return list(self._action_plans.values())

    async def get_strategic_health(self) -> Dict[str, Any]:
        return {
            "decisions_made": len(self._decisions),
            "active_plans": len(self._action_plans),
            "strategy_alignment": 0.85,
            "execution_progress": 0.62,
        }
