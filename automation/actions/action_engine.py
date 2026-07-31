"""Action engine: facade for the actions subsystem."""

from __future__ import annotations

from typing import Any, Callable

from automation.actions.action_builder import ActionBuilder
from automation.actions.action_models import (ActionDefinition,
                                              ActionResult)
from automation.actions.action_policy import ActionPolicy
from automation.actions.action_registry import ActionRegistry
from automation.actions.action_router import ActionRouter
from automation.actions.action_runner import ActionRunner
from automation.actions.action_validator import ActionValidator
from automation.automation_events import AutomationEventType


class ActionEngine:
    """Registers and executes actions with validation, policy, and retries."""

    def __init__(self, registry: ActionRegistry | None = None,
                 runner: ActionRunner | None = None,
                 validator: ActionValidator | None = None,
                 policy: ActionPolicy | None = None,
                 router: ActionRouter | None = None,
                 events: Any = None, metrics: Any = None) -> None:
        self.registry = registry or ActionRegistry()
        self.validator = validator or ActionValidator()
        self.policy = policy or ActionPolicy()
        self.router = router or ActionRouter(self.registry)
        self.runner = runner or ActionRunner(self.registry)
        self.events = events
        self.metrics = metrics
        self._history: list[ActionResult] = []

    # -- registration ------------------------------------------------------
    def build(self) -> ActionBuilder:
        return ActionBuilder()

    def register(self, definition: ActionDefinition,
                 handler: Callable[[dict[str, Any]], Any] | None = None,
                 ) -> list[str] | None:
        issues = self.validator.validate_definition(definition)
        if issues:
            return issues
        self.registry.register(definition, handler)
        return None

    def has(self, action_id: str) -> bool:
        return self.registry.has(action_id)

    def list(self) -> list[str]:
        return self.registry.list()

    def remove(self, action_id: str) -> bool:
        return self.registry.remove(action_id)

    def get(self, action_id: str) -> ActionDefinition | None:
        return self.registry.get_definition(action_id)

    # -- execution ---------------------------------------------------------
    def execute(self, action_id: str, params: dict[str, Any] | None = None,
                fallback: Callable[[str, dict[str, Any]], Any] | None = None,
                ) -> ActionResult:
        values = dict(params or {})
        definition = self.registry.get_definition(action_id)
        if definition is None:
            return self._handle_unknown(action_id, values, fallback)
        if not definition.enabled:
            result = ActionResult(action_id, False, error="action disabled")
            self._record(result)
            return result

        blocked = self.policy.reason(action_id)
        if blocked is not None:
            result = ActionResult(action_id, False,
                                  error=f"policy blocked: {blocked}")
            self._record(result)
            return result

        issues = self.validator.validate_params(definition, values)
        if issues:
            result = ActionResult(action_id, False, error="; ".join(issues))
            self._record(result)
            return result

        values = self.validator.coerce_params(definition, values)
        result = self.runner.run(definition, values)
        if result.success:
            self.policy.record_call(action_id)
        self._record(result)
        return result

    def _handle_unknown(self, action_id: str, params: dict[str, Any],
                        fallback: Callable[[str, dict[str, Any]], Any] | None,
                        ) -> ActionResult:
        try:
            if self.router.can_route(action_id):
                result = self.router.route(action_id, params)
                return ActionResult(action_id, True, result=result)
            if fallback is not None:
                return ActionResult(action_id, True,
                                    result=fallback(action_id, params))
        except Exception as exc:  # noqa: BLE001
            return ActionResult(action_id, False, error=str(exc))
        return ActionResult(action_id, False,
                            error=f"unknown action: {action_id}")

    def history(self, limit: int = 50) -> list[ActionResult]:
        return list(self._history[-limit:])

    def _record(self, result: ActionResult) -> None:
        self._history.append(result)
        if self.events is not None:
            event_type = (AutomationEventType.TASK_COMPLETED if result.success
                          else AutomationEventType.TASK_FAILED)
            self.events.publish(event_type,
                                {"action_id": result.action_id,
                                 "success": result.success})
        if self.metrics is not None:
            self.metrics.increment("actions.completed" if result.success
                                   else "actions.failed")
