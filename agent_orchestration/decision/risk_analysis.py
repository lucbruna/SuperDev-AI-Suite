"""Risk analysis for tasks and actions (Volume 31)."""

from __future__ import annotations

from typing import Any

from agent_orchestration.orchestrator_models import AgentTask, RiskLevel


class RiskAnalyzer:
    """Assesses risk from task attributes and agent permissions."""

    def assess(self, task: AgentTask,
               permissions: list[str] | None = None) -> dict[str, Any]:
        reasons: list[str] = []
        level = task.risk_level

        if task.approval_required:
            reasons.append("approval_required")
        if task.attempts > 0:
            reasons.append("retrying")
            level = self._raise_(level)
        if task.dependencies:
            reasons.append("has_dependencies")
        permissions = permissions or []
        if "*" in permissions or "dangerous" in permissions:
            reasons.append("broad_permissions")
            level = self._raise_(level)

        return {"level": level, "reasons": reasons}

    @staticmethod
    def _raise_(level: RiskLevel) -> RiskLevel:
        order = [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH,
                 RiskLevel.CRITICAL]
        index = order.index(level)
        return order[min(index + 1, len(order) - 1)]
