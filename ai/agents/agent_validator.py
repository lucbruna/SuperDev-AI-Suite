from __future__ import annotations

from typing import Any


class AgentValidator:
    """Validates agent configurations and tasks."""

    @staticmethod
    def validate_agent_id(agent_id: Any) -> bool:
        return isinstance(agent_id, str) and len(agent_id) > 0

    @staticmethod
    def validate_task(task: dict[str, Any]) -> bool:
        return isinstance(task, dict) and "type" in task

    @staticmethod
    def validate_config(config: dict[str, Any]) -> bool:
        return isinstance(config, dict)
