from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..decision_config import DecisionConfig
from ..decision_models import ActionPlan, DecisionStatus, Recommendation

logger = logging.getLogger(__name__)


class ActionPlanner:
    def __init__(self, config: DecisionConfig):
        self._config = config
        self._plans: Dict[str, ActionPlan] = {}

    def create_plan(self, title: str, recommendations: List[Recommendation]) -> ActionPlan:
        plan = ActionPlan(
            id=str(uuid.uuid4()),
            title=title,
            recommendations=recommendations,
            total_effort_hours=sum(r.effort_hours for r in recommendations),
            total_roi=sum(r.roi_estimate for r in recommendations),
            priority_score=sum(r.roi_estimate for r in recommendations) / max(len(recommendations), 1),
        )
        self._plans[plan.id] = plan
        return plan

    def get_plan(self, plan_id: str) -> Optional[ActionPlan]:
        return self._plans.get(plan_id)

    def update_status(self, plan_id: str, status: DecisionStatus) -> Optional[ActionPlan]:
        plan = self._plans.get(plan_id)
        if plan:
            plan.status = status
        return plan

    def list_plans(self, status: Optional[DecisionStatus] = None) -> List[ActionPlan]:
        if status:
            return [p for p in self._plans.values() if p.status == status]
        return list(self._plans.values())

    def prioritize(self, plans: List[ActionPlan]) -> List[ActionPlan]:
        return sorted(plans, key=lambda p: p.priority_score, reverse=True)
