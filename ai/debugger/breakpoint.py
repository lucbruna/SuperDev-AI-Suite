from __future__ import annotations

from enum import Enum
from typing import Any


class BreakpointType(Enum):
    NODE_ENTRY = "node_entry"
    NODE_EXIT = "node_exit"
    CONDITIONAL = "conditional"
    VARIABLE_WATCH = "variable_watch"
    ERROR = "error"
    LINE = "line"


class BreakpointCondition:
    def __init__(self, field: str, operator: str, value: Any):
        self.field = field
        self.operator = operator
        self.value = value

    def evaluate(self, context: dict[str, Any]) -> bool:
        actual = context
        for part in self.field.split("."):
            if isinstance(actual, dict):
                actual = actual.get(part)
            else:
                return False
        if self.operator == "==":
            return actual == self.value
        if self.operator == "!=":
            return actual != self.value
        if self.operator == ">" and isinstance(actual, (int, float)):
            return actual > self.value
        if self.operator == "<" and isinstance(actual, (int, float)):
            return actual < self.value
        if self.operator == ">=" and isinstance(actual, (int, float)):
            return actual >= self.value
        if self.operator == "<=" and isinstance(actual, (int, float)):
            return actual <= self.value
        if self.operator == "contains" and isinstance(actual, str):
            return str(self.value) in actual
        if self.operator == "in" and isinstance(self.value, (list, tuple)):
            return actual in self.value
        if self.operator == "regex" and isinstance(actual, str):
            import re
            return bool(re.search(str(self.value), actual))
        return False


class Breakpoint:
    def __init__(
        self,
        bp_type: BreakpointType = BreakpointType.NODE_ENTRY,
        node_id: str = "",
        condition: BreakpointCondition | None = None,
        enabled: bool = True,
        hit_count: int = 0,
        max_hits: int = 0,
    ):
        self.bp_type = bp_type
        self.node_id = node_id
        self.condition = condition
        self.enabled = enabled
        self.hit_count = hit_count
        self.max_hits = max_hits
        self.id: str = ""

    def __post_init__(self):
        import uuid
        self.id = str(uuid.uuid4())[:12]

    def should_break(self, context: dict[str, Any]) -> bool:
        if not self.enabled:
            return False
        if self.max_hits > 0 and self.hit_count >= self.max_hits:
            return False
        if self.condition:
            return self.condition.evaluate(context)
        return True

    def hit(self) -> None:
        self.hit_count += 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.bp_type.value,
            "node_id": self.node_id,
            "enabled": self.enabled,
            "hit_count": self.hit_count,
            "max_hits": self.max_hits,
            "condition": {
                "field": self.condition.field,
                "operator": self.condition.operator,
                "value": str(self.condition.value),
            } if self.condition else None,
        }


class BreakpointManager:
    def __init__(self):
        self._breakpoints: dict[str, Breakpoint] = {}
        self._node_breakpoints: dict[str, list[str]] = {}

    def add(self, bp: Breakpoint) -> str:
        self._breakpoints[bp.id] = bp
        if bp.node_id:
            if bp.node_id not in self._node_breakpoints:
                self._node_breakpoints[bp.node_id] = []
            self._node_breakpoints[bp.node_id].append(bp.id)
        return bp.id

    def remove(self, bp_id: str) -> None:
        bp = self._breakpoints.pop(bp_id, None)
        if bp and bp.node_id:
            node_bps = self._node_breakpoints.get(bp.node_id, [])
            if bp_id in node_bps:
                node_bps.remove(bp_id)

    def toggle(self, bp_id: str) -> None:
        bp = self._breakpoints.get(bp_id)
        if bp:
            bp.enabled = not bp.enabled

    def get(self, bp_id: str) -> Breakpoint | None:
        return self._breakpoints.get(bp_id)

    def list_all(self) -> list[Breakpoint]:
        return list(self._breakpoints.values())

    def get_for_node(self, node_id: str) -> list[Breakpoint]:
        bp_ids = self._node_breakpoints.get(node_id, [])
        return [self._breakpoints[bp_id] for bp_id in bp_ids if bp_id in self._breakpoints]

    def check_node(self, node_id: str, context: dict[str, Any]) -> list[Breakpoint]:
        triggered: list[Breakpoint] = []
        for bp in self.get_for_node(node_id):
            if bp.should_break(context):
                bp.hit()
                triggered.append(bp)
        return triggered

    def clear_all(self) -> None:
        self._breakpoints.clear()
        self._node_breakpoints.clear()

    @property
    def count(self) -> int:
        return len(self._breakpoints)
