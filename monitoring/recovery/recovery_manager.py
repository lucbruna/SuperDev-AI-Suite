from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable

from ..monitoring_models import RecoveryAction


@dataclass
class RecoveryManagerConfig:
    max_concurrent: int = 5
    default_timeout: float = 30.0
    auto_retry: bool = True
    max_retries: int = 3


class RecoveryManager:
    """Coordinates recovery actions across components."""

    def __init__(self, config: RecoveryManagerConfig | None = None) -> None:
        self._config = config or RecoveryManagerConfig()
        self._actions: dict[str, RecoveryAction] = {}
        self._strategies: dict[str, Callable[[RecoveryAction], None]] = {}
        self._history: list[RecoveryAction] = []

    def register_strategy(self, action_type: str, handler: Callable[[RecoveryAction], None]) -> None:
        self._strategies[action_type] = handler

    def execute(self, action_type: str, target: str, reason: str = "") -> RecoveryAction:
        action = RecoveryAction(
            action_id=uuid.uuid4().hex[:12],
            action_type=action_type,
            target=target,
            reason=reason,
        )
        self._actions[action.action_id] = action
        self._execute_action(action)
        return action

    def _execute_action(self, action: RecoveryAction) -> None:
        strategy = self._strategies.get(action.action_type)
        if not strategy:
            action.status = "failed"
            action.reason = f"No strategy registered for '{action.action_type}'"
            action.completed_at = time.time()
            self._history.append(action)
            return

        action.status = "running"
        try:
            strategy(action)
            action.status = "succeeded"
        except Exception as e:
            action.status = "failed"
            action.reason = f"{action.reason}; {e}"
        action.completed_at = time.time()
        self._history.append(action)

    def get_action(self, action_id: str) -> RecoveryAction | None:
        return self._actions.get(action_id)

    def get_history(self, limit: int = 100) -> list[RecoveryAction]:
        return list(self._history[-limit:])

    def summary(self) -> dict[str, Any]:
        total = len(self._history)
        succeeded = sum(1 for a in self._history if a.status == "succeeded")
        failed = sum(1 for a in self._history if a.status == "failed")
        return {
            "total": total,
            "succeeded": succeeded,
            "failed": failed,
            "success_rate": round(succeeded / max(total, 1) * 100, 1),
            "active": len([a for a in self._actions.values() if a.status == "running"]),
        }
