"""ModuleLifecycle: state machine for module status transitions."""
from __future__ import annotations

from typing import Any, Callable, Optional

MODULE_STATES = ("registered", "loading", "active", "inactive", "failed", "unloaded")

MODULE_TRANSITIONS: dict[str, tuple[str, ...]] = {
    "registered": ("loading", "inactive", "unloaded", "failed"),
    "loading": ("active", "failed", "inactive"),
    "active": ("inactive", "failed", "unloaded"),
    "inactive": ("loading", "unloaded", "failed"),
    "failed": ("registered", "unloaded"),
    "unloaded": ("registered",),
}


class ModuleLifecycle:
    """Validated state transitions with a deterministic event log."""

    def __init__(
        self, on_transition: Optional[Callable[[str, Optional[str], str], None]] = None
    ) -> None:
        self._states: dict[str, str] = {}
        self._events: list[dict[str, Any]] = []
        self.on_transition = on_transition

    def state(self, module_id: str) -> Optional[str]:
        return self._states.get(module_id)

    def set_state(self, module_id: str, state: str) -> bool:
        if state not in MODULE_STATES:
            raise ValueError(f"invalid module state {state!r}; expected one of {MODULE_STATES}")
        current = self._states.get(module_id)
        if current is None or state in MODULE_TRANSITIONS.get(current, ()):
            self._states[module_id] = state
            self._events.append(
                {"module_id": module_id, "from": current, "to": state, "ok": True}
            )
            if self.on_transition is not None:
                self.on_transition(module_id, current, state)
            return True
        self._events.append(
            {"module_id": module_id, "from": current, "to": state, "ok": False}
        )
        return False

    def can_transition(self, current: str, target: str) -> bool:
        return target in MODULE_TRANSITIONS.get(current, ())

    def events(self) -> list[dict[str, Any]]:
        return list(self._events)
