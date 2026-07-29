"""
Decision Manager - Handles critical decision making with governance
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from enterprise_ai_core.models import (
    Decision,
    PolicyEvaluation,
    Event,
    EventType,
    Severity,
)
from enterprise_ai_core.policy_engine import PolicyEngine


class DecisionManager:
    """Manages critical decisions requiring governance oversight"""

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.config = orchestrator.config
        self.policy_engine = orchestrator.policy_engine
        self._decision_history: List[Decision] = []
        self._pending_approvals: Dict[UUID, Dict] = {}
        self._decision_handlers: Dict[str, callable] = {}

    async def initialize(self) -> None:
        pass

    async def shutdown(self) -> None:
        pass

    async def make_decision(
        self,
        context: Dict[str, Any],
        options: List[Dict[str, Any]],
        criteria: Optional[Dict[str, Any]] = None,
        requires_approval: bool = False,
        approvers: Optional[List[str]] = None,
    ) -> Decision:
        """Make a decision based on context, options, and criteria"""

        policy_evals = []
        for option in options:
            eval_result = await self.policy_engine.evaluate(
                action="decision_option",
                context={**context, "option": option},
            )
            policy_evals.append(eval_result)

        allowed_options = [
            opt for opt, eval_result in zip(options, policy_evals)
            if eval_result.action.value in ("allow", "log_only")
        ]

        if not allowed_options:
            allowed_options = options

        selected = self._select_best_option(allowed_options, criteria or {}, context)

        decision = Decision(
            context=context,
            options=options,
            selected_option=selected,
            rationale=self._generate_rationale(selected, allowed_options, criteria),
            confidence=self._calculate_confidence(selected, allowed_options, context),
            policy_evaluations=policy_evals,
        )

        if requires_approval or any(e.action.value == "require_approval" for e in policy_evals):
            decision.metadata["requires_approval"] = True
            decision.metadata["approvers"] = approvers or ["governance_board"]
            await self._request_approval(decision)

        self._decision_history.append(decision)

        await self.orchestrator.publish_event(
            Event(
                type=EventType.DECISION_MADE,
                payload={
                    "decision_id": str(decision.id),
                    "selected": selected,
                    "confidence": decision.confidence,
                    "requires_approval": decision.metadata.get("requires_approval", False),
                },
            )
        )

        return decision

    def _select_best_option(
        self,
        options: List[Dict[str, Any]],
        criteria: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        if not options:
            return {}

        if len(options) == 1:
            return options[0]

        scored = []
        for option in options:
            score = 0.0
            for criterion, weight in criteria.items():
                if criterion in option:
                    score += self._score_criterion(option[criterion], criterion) * weight
            scored.append((score, option))

        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1] if scored else options[0]

    def _score_criterion(self, value: Any, criterion: str) -> float:
        if isinstance(value, (int, float)):
            return float(value)
        elif isinstance(value, bool):
            return 1.0 if value else 0.0
        elif isinstance(value, str):
            return 1.0
        return 0.5

    def _generate_rationale(
        self,
        selected: Dict[str, Any],
        allowed: List[Dict[str, Any]],
        criteria: Dict[str, Any],
    ) -> str:
        if not selected:
            return "No valid options available"

        reasons = [f"Selected option: {selected.get('name', 'unnamed')}"]

        if criteria:
            criteria_met = [k for k, v in criteria.items() if selected.get(k) == v]
            if criteria_met:
                reasons.append(f"Meets criteria: {', '.join(criteria_met)}")

        if len(allowed) > 1:
            reasons.append(f"Chosen from {len(allowed)} allowed options")

        return ". ".join(reasons)

    def _calculate_confidence(
        self,
        selected: Dict[str, Any],
        allowed: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> float:
        if not selected:
            return 0.0

        base_confidence = 0.8

        if len(allowed) == 1:
            base_confidence += 0.1

        policy_blocked = len([o for o in allowed if o != selected])
        base_confidence -= policy_blocked * 0.05

        return max(0.0, min(1.0, base_confidence))

    async def _request_approval(self, decision: Decision) -> None:
        approval_id = uuid4()
        self._pending_approvals[approval_id] = {
            "decision": decision,
            "status": "pending",
            "requested_at": datetime.utcnow(),
        }

        await self.orchestrator.publish_event(
            Event(
                type=EventType.DECISION_MADE,
                severity=Severity.WARNING,
                payload={
                    "decision_id": str(decision.id),
                    "approval_id": str(approval_id),
                    "status": "awaiting_approval",
                    "approvers": decision.metadata.get("approvers", []),
                },
            )
        )

    async def submit_approval(
        self,
        approval_id: UUID,
        approved: bool,
        approver_id: UUID,
        comments: str = "",
    ) -> bool:
        approval = self._pending_approvals.get(approval_id)
        if not approval:
            return False

        approval["status"] = "approved" if approved else "rejected"
        approval["approver_id"] = approver_id
        approval["comments"] = comments
        approval["decided_at"] = datetime.utcnow()

        decision = approval["decision"]
        decision.metadata["approval_result"] = approval["status"]
        decision.metadata["approver"] = str(approver_id)

        return True

    def get_decision_history(self, limit: int = 100) -> List[Decision]:
        return self._decision_history[-limit:]

    def get_pending_approvals(self) -> List[Dict]:
        return [
            {"approval_id": str(k), **v}
            for k, v in self._pending_approvals.items()
            if v["status"] == "pending"
        ]

    def register_decision_handler(self, decision_type: str, handler: callable) -> None:
        self._decision_handlers[decision_type] = handler