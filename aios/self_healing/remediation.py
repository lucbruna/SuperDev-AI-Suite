"""Remediation: ordered healing actions executed to recover from failures."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

#: action: (context) -> bool
RemediationFn = Callable[[dict[str, Any]], bool]


@dataclass
class RemediationAction:
    action_id: str
    execute: RemediationFn
    description: str = ""


@dataclass
class RemediationOutcome:
    ok: bool
    applied: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "applied": list(self.applied),
            "errors": list(self.errors),
        }


class RemediationPlan:
    """Runs actions in declaration order; stops on the first failure."""

    def __init__(
        self, plan_id: str, actions: list[RemediationAction] | None = None
    ) -> None:
        self.plan_id = plan_id
        self.actions = list(actions or [])

    def execute(self, context: dict[str, Any] | None = None) -> RemediationOutcome:
        outcome = RemediationOutcome(ok=True)
        ctx = dict(context or {})
        for action in self.actions:
            try:
                ok = bool(action.execute(ctx))
            except Exception as exc:  # noqa: BLE001 - isolate action failures
                ok = False
                outcome.errors.append(f"{action.action_id}: {exc}")
            if ok:
                outcome.applied.append(action.action_id)
            else:
                outcome.ok = False
                outcome.errors.append(f"{action.action_id}: remediation failed")
                break
        return outcome

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "actions": [action.action_id for action in self.actions],
        }
