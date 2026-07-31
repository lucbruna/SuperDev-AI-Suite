"""Automation engine configuration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AutomationConfig:
    """Global configuration for the automation engine."""

    workspace: str = "default"
    max_retries: int = 3
    retry_delay: float = 1.0
    default_timeout: float = 60.0
    max_concurrent_tasks: int = 10
    history_limit: int = 1000
    security_level: str = "standard"  # standard | strict
    settings: dict[str, Any] = field(default_factory=dict)

    def merge(self, **overrides: Any) -> "AutomationConfig":
        """Returns a copy merged with the given overrides."""
        config = AutomationConfig(
            workspace=overrides.get("workspace", self.workspace),
            max_retries=overrides.get("max_retries", self.max_retries),
            retry_delay=overrides.get("retry_delay", self.retry_delay),
            default_timeout=overrides.get("default_timeout", self.default_timeout),
            max_concurrent_tasks=overrides.get(
                "max_concurrent_tasks", self.max_concurrent_tasks),
            history_limit=overrides.get("history_limit", self.history_limit),
            security_level=overrides.get("security_level", self.security_level),
            settings={**self.settings, **overrides.get("settings", {})},
        )
        return config

    def to_dict(self) -> dict[str, Any]:
        return {
            "workspace": self.workspace,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "default_timeout": self.default_timeout,
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "history_limit": self.history_limit,
            "security_level": self.security_level,
            "settings": dict(self.settings),
        }
