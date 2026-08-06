"""Repair execution: deterministic simulation of controlled fixes."""
from __future__ import annotations

from dataclasses import dataclass

from modules.self_healing_engine.config.constants import (
    REPAIR_APPROVED,
    REPAIR_PENDING,
    REPAIR_ROLLED_BACK,
    REPAIR_SKIPPED,
    REPAIR_SUCCEEDED,
)
from modules.self_healing_engine.config.repair_rules import RepairRulesConfig
from modules.self_healing_engine.config.security_policy import SecurityPolicy
from modules.self_healing_engine.core.healing_context import HealingContext
from modules.self_healing_engine.repair.planner import RepairPlan


@dataclass(slots=True)
class RepairOutcome:
    """Outcome of executing a repair plan."""

    plan_kind: str
    target: str
    status: str
    attempts: int
    message: str = ""
    rolled_back: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "plan_kind": self.plan_kind,
            "target": self.target,
            "status": self.status,
            "attempts": self.attempts,
            "message": self.message,
            "rolled_back": self.rolled_back,
        }


class RepairExecutor:
    """Executes plans respecting approval and security policies.

    Deterministic: repair steps are symbolic instructions recorded in the
    healing memory; no real commands are run.
    """

    def __init__(
        self,
        rules: RepairRulesConfig | None = None,
        security_policy: SecurityPolicy | None = None,
    ) -> None:
        self._rules = rules or RepairRulesConfig()
        self._security_policy = security_policy or SecurityPolicy()

    def execute(self, plan: RepairPlan, ctx: HealingContext) -> RepairOutcome:
        if plan.requires_approval:
            outcome = RepairOutcome(
                plan_kind=plan.kind,
                target=plan.target,
                status=REPAIR_PENDING,
                attempts=0,
                message="approval required",
            )
            ctx.publish("repair.awaiting_approval", outcome.to_dict())
            return outcome

        for step in plan.steps:
            if self._security_policy.contains_forbidden_pattern(step):
                outcome = RepairOutcome(
                    plan_kind=plan.kind,
                    target=plan.target,
                    status=REPAIR_SKIPPED,
                    attempts=1,
                    message="step rejected by security policy",
                )
                ctx.publish("repair.skipped", outcome.to_dict())
                self._notify_failure(ctx, outcome)
                return outcome

        ctx.memory.remember(f"repair:{plan.target}", plan.to_dict())
        outcome = RepairOutcome(
            plan_kind=plan.kind,
            target=plan.target,
            status=REPAIR_SUCCEEDED,
            attempts=1,
            message="repair executed",
        )
        ctx.publish("repair.executed", outcome.to_dict())
        return outcome

    def approve(self, plan: RepairPlan, ctx: HealingContext) -> RepairOutcome:
        ctx.memory.remember(f"repair:{plan.target}:approved", plan.to_dict())
        outcome = RepairOutcome(
            plan_kind=plan.kind,
            target=plan.target,
            status=REPAIR_APPROVED,
            attempts=0,
            message="approved by operator",
        )
        ctx.publish("repair.approved", outcome.to_dict())
        return outcome

    def rollback(self, plan: RepairPlan, ctx: HealingContext) -> RepairOutcome:
        outcome = RepairOutcome(
            plan_kind=plan.kind,
            target=plan.target,
            status=REPAIR_ROLLED_BACK,
            attempts=0,
            message="rolled back",
            rolled_back=True,
        )
        ctx.publish("repair.rolled_back", outcome.to_dict())
        return outcome

    def _notify_failure(self, ctx: HealingContext, outcome: RepairOutcome) -> None:
        if self._rules.notify_on_failure:
            ctx.publish("repair.failed", outcome.to_dict())
