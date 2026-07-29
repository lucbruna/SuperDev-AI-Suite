import uuid
import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AlertRule(BaseModel):
    name: str
    condition: str  # e.g. "cpu_percent > 90"
    severity: str = "warning"
    duration_seconds: float = 0.0
    channels: List[str] = Field(default_factory=list)


class TriggeredAlert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    rule_name: str
    condition: str
    severity: str
    message: str
    timestamp: float = Field(default_factory=time.time)
    value: float = 0.0
    metric: str = ""
    threshold: float = 0.0


class RuleEngine:
    def __init__(self) -> None:
        self._alert_history: Dict[str, float] = {}

    def evaluate(self, rules: List[AlertRule], metrics: Dict[str, float]) -> List[TriggeredAlert]:
        triggered: List[TriggeredAlert] = []
        now = time.time()

        for rule in rules:
            parts = rule.condition.split()
            if len(parts) != 3:
                continue
            metric_name, operator, threshold_str = parts
            try:
                threshold = float(threshold_str)
            except ValueError:
                continue

            value = metrics.get(metric_name)
            if value is None:
                continue

            matched = False
            if operator == ">":
                matched = value > threshold
            elif operator == "<":
                matched = value < threshold
            elif operator == ">=":
                matched = value >= threshold
            elif operator == "<=":
                matched = value <= threshold
            elif operator == "==":
                matched = value == threshold

            if matched:
                last_triggered = self._alert_history.get(rule.name, 0.0)
                if (now - last_triggered) >= rule.duration_seconds:
                    self._alert_history[rule.name] = now
                    triggered.append(
                        TriggeredAlert(
                            rule_name=rule.name,
                            condition=rule.condition,
                            severity=rule.severity,
                            message=f"Rule '{rule.name}' triggered: {rule.condition}",
                            value=value,
                            metric=metric_name,
                            threshold=threshold,
                        )
                    )
        return triggered
