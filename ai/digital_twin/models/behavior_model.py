"""Behavior model."""
from __future__ import annotations
from typing import Any, Dict, List
import time, uuid

class BehaviorModel:
    def __init__(self) -> None:
        self._behaviors: Dict[str, Dict[str, Any]] = {}
    def create(self, name: str, rules: List[Dict[str, Any]], entity_type: str = "generic") -> Dict[str, Any]:
        behavior_id = str(uuid.uuid4())[:8]
        behavior = {"behavior_id": behavior_id, "name": name, "rules": rules, "entity_type": entity_type, "created_at": time.time()}
        self._behaviors[behavior_id] = behavior
        return behavior
    def get(self, behavior_id: str) -> Dict[str, Any]:
        return self._behaviors.get(behavior_id, {"error": "not_found"})
    def add_rule(self, behavior_id: str, rule: Dict[str, Any]) -> bool:
        if behavior_id not in self._behaviors:
            return False
        self._behaviors[behavior_id]["rules"].append(rule)
        return True
    def evaluate(self, behavior_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if behavior_id not in self._behaviors:
            return {"error": "not_found"}
        behavior = self._behaviors[behavior_id]
        triggered = []
        for rule in behavior["conditions"] if "conditions" in behavior else behavior.get("rules", []):
            condition = rule.get("condition", "")
            if condition and condition.lower() in str(context).lower():
                triggered.append(rule.get("action", "no_action"))
        return {"behavior_id": behavior_id, "triggered_actions": triggered}
    def list_all(self) -> List[Dict[str, Any]]:
        return list(self._behaviors.values())
    def count(self) -> int:
        return len(self._behaviors)
