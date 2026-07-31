"""Configuration for the Agent Orchestration Engine (Volume 31)."""

from __future__ import annotations

from typing import Any


class OrchestratorConfig:
    """Runtime configuration for the orchestrator and its agents."""

    def __init__(self, max_agents: int = 50,
                 task_timeout: float = 60.0,
                 max_retries: int = 2,
                 default_priority: str = "medium",
                 require_approval_for_high_risk: bool = True,
                 auto_learn: bool = True,
                 log_level: str = "INFO",
                 **overrides: Any) -> None:
        self.max_agents = int(max_agents)
        self.task_timeout = float(task_timeout)
        self.max_retries = int(max_retries)
        self.default_priority = default_priority
        self.require_approval_for_high_risk = bool(
            require_approval_for_high_risk)
        self.auto_learn = bool(auto_learn)
        self.log_level = log_level
        for key, value in overrides.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)

    def merge(self, updates: dict[str, Any] | None) -> "OrchestratorConfig":
        for key, value in (updates or {}).items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self

    def snapshot(self) -> dict[str, Any]:
        return {
            "max_agents": self.max_agents,
            "task_timeout": self.task_timeout,
            "max_retries": self.max_retries,
            "default_priority": self.default_priority,
            "require_approval_for_high_risk": (
                self.require_approval_for_high_risk),
            "auto_learn": self.auto_learn,
            "log_level": self.log_level,
        }
