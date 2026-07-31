"""Handler for deployment rollbacks."""
from datetime import datetime
from typing import Any

from .models import Deployment, DeploymentStatus, RollbackPlan


class RollbackHandler:
    """Handles deployment rollbacks."""

    def __init__(self):
        self._plans: dict[str, RollbackPlan] = {}
        self._rollback_history: list[dict[str, Any]] = []

    def create_plan(self, deployment_id: str, steps: list[str],
                    triggers: list[str] = None) -> RollbackPlan:
        plan = RollbackPlan(
            deployment_id=deployment_id,
            steps=steps,
            triggers=triggers or [],
        )
        self._plans[plan.plan_id] = plan
        return plan

    def execute_rollback(self, deployment: Deployment, plan: RollbackPlan = None) -> bool:
        if not plan:
            plan = self._plans.get(deployment.deployment_id)

        deployment.status = DeploymentStatus.ROLLED_BACK
        self._rollback_history.append({
            "deployment_id": deployment.deployment_id,
            "plan_id": plan.plan_id if plan else None,
            "timestamp": datetime.utcnow().isoformat(),
        })
        return True

    def get_plan(self, plan_id: str) -> RollbackPlan | None:
        return self._plans.get(plan_id)

    def get_plan_for_deployment(self, deployment_id: str) -> RollbackPlan | None:
        for plan in self._plans.values():
            if plan.deployment_id == deployment_id:
                return plan
        return None

    def get_history(self) -> list[dict[str, Any]]:
        return list(self._rollback_history)

    def list_plans(self) -> list[RollbackPlan]:
        return list(self._plans.values())
