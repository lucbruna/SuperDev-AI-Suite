"""Alert Rules - Notification trigger rules."""
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class AlertCondition(Enum):
    THRESHOLD = "threshold"
    CHANGE = "change"
    PATTERN = "pattern"
    ABSENCE = "absence"
    PRESENCE = "presence"


@dataclass
class AlertRule:
    rule_id: str
    name: str
    condition: AlertCondition = AlertCondition.THRESHOLD
    metric: str = ""
    threshold: float = 0.0
    operator: str = ">"
    notification_title: str = ""
    notification_message: str = ""
    enabled: bool = True
    cooldown_seconds: int = 300
    last_triggered: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class AlertRuleManager:
    def __init__(self):
        self.rules: dict[str, AlertRule] = {}
        self.trigger_log: list[dict[str, Any]] = []

    def create_rule(self, name: str, condition: AlertCondition, metric: str = "", threshold: float = 0.0, operator: str = ">", **kwargs) -> AlertRule:
        rule_id = hashlib.sha256(f"{name}{metric}".encode()).hexdigest()[:16]
        rule = AlertRule(rule_id=rule_id, name=name, condition=condition, metric=metric, threshold=threshold, operator=operator, **kwargs)
        self.rules[rule_id] = rule
        return rule

    def evaluate(self, rule_id: str, current_value: float) -> bool:
        rule = self.rules.get(rule_id)
        if not rule or not rule.enabled:
            return False
        if rule.operator == ">":
            triggered = current_value > rule.threshold
        elif rule.operator == "<":
            triggered = current_value < rule.threshold
        elif rule.operator == "==":
            triggered = current_value == rule.threshold
        elif rule.operator == ">=":
            triggered = current_value >= rule.threshold
        elif rule.operator == "<=":
            triggered = current_value <= rule.threshold
        else:
            triggered = False
        if triggered:
            rule.last_triggered = datetime.now()
            self.trigger_log.append({"rule_id": rule_id, "value": current_value, "timestamp": datetime.now().isoformat()})
        return triggered

    def get_rule(self, rule_id: str) -> AlertRule | None:
        return self.rules.get(rule_id)

    def list_rules(self, enabled_only: bool = False) -> list[AlertRule]:
        rules = list(self.rules.values())
        if enabled_only:
            rules = [r for r in rules if r.enabled]
        return rules

    def count(self) -> int:
        return len(self.rules)
