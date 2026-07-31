"""Behavior model."""

from __future__ import annotations

import time
import uuid
from typing import Any


class BehaviorModel:
    def __init__(self) -> None:
        self._behaviors: dict[str, dict[str, Any]] = {}

    def create(self, name: str, rules: list[dict[str, Any]], entity_type: str = "generic") -> dict[str, Any]:
        behavior_id = str(uuid.uuid4())[:8]
        behavior = {
            "behavior_id": behavior_id,
            "name": name,
            "rules": rules,
            "entity_type": entity_type,
            "created_at": time.time(),
        }
        self._behaviors[behavior_id] = behavior
        return behavior

    def get(self, behavior_id: str) -> dict[str, Any]:
        return self._behaviors.get(behavior_id, {"error": "not_found"})

    def add_rule(self, behavior_id: str, rule: dict[str, Any]) -> bool:
        if behavior_id not in self._behaviors:
            return False
        self._behaviors[behavior_id]["rules"].append(rule)
        return True

    def evaluate(self, behavior_id: str, context: dict[str, Any]) -> dict[str, Any]:
        if behavior_id not in self._behaviors:
            return {"error": "not_found"}
        behavior = self._behaviors[behavior_id]
        triggered = []
        for rule in behavior["conditions"] if "conditions" in behavior else behavior.get("rules", []):
            condition = rule.get("condition", "")
            if condition and condition.lower() in str(context).lower():
                triggered.append(rule.get("action", "no_action"))
        return {"behavior_id": behavior_id, "triggered_actions": triggered}

    def list_all(self) -> list[dict[str, Any]]:
        return list(self._behaviors.values())

    def count(self) -> int:
        return len(self._behaviors)
