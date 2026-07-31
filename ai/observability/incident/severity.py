"""Incident severity."""

from __future__ import annotations

from enum import Enum
from typing import Any


class IncidentSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SeverityManager:
    def __init__(self) -> None:
        self._levels: dict[str, dict[str, Any]] = {
            "low": {"label": "Low", "response_time": 24, "escalation": False},
            "medium": {"label": "Medium", "response_time": 4, "escalation": True},
            "high": {"label": "High", "response_time": 1, "escalation": True},
            "critical": {"label": "Critical", "response_time": 0.25, "escalation": True},
        }

    def get_level(self, severity: str) -> dict[str, Any]:
        return self._levels.get(severity, self._levels["low"])

    def set_level(self, severity: str, config: dict[str, Any]) -> None:
        self._levels[severity] = config

    def get_response_time(self, severity: str) -> float:
        return self.get_level(severity).get("response_time", 24)

    def should_escalate(self, severity: str) -> bool:
        return self.get_level(severity).get("escalation", False)

    def list_levels(self) -> dict[str, dict[str, Any]]:
        return dict(self._levels)

    def add_level(self, name: str, label: str, response_time: float, escalation: bool = False) -> None:
        self._levels[name] = {"label": label, "response_time": response_time, "escalation": escalation}

    def remove_level(self, name: str) -> bool:
        if name in self._levels:
            del self._levels[name]
            return True
        return False
