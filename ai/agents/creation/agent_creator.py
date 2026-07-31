"""Agent creation from templates and configurations."""

from __future__ import annotations

import time
import uuid
from typing import Any


class AgentCreator:
    """Creates agent instances from templates and configurations."""

    def __init__(self) -> None:
        self._created_agents: dict[str, dict[str, Any]] = {}
        self._creation_count: int = 0

    def create_agent(
        self,
        name: str,
        agent_type: str,
        config: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        agent_id = f"agent_{uuid.uuid4().hex[:12]}"
        agent = {
            "agent_id": agent_id,
            "name": name,
            "type": agent_type,
            "config": config or {},
            "status": "created",
            "created_at": time.time(),
            "version": "1.0.0",
        }
        self._created_agents[agent_id] = agent
        self._creation_count += 1
        return agent

    def create_from_template(
        self,
        template_name: str,
        overrides: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        from .template_manager import TemplateManager

        mgr = TemplateManager()
        template = mgr.get_template(template_name)
        if template is None:
            return {"error": f"Template '{template_name}' not found"}
        merged = {**template, **(overrides or {})}
        name = merged.pop("name", template_name)
        agent_type = merged.pop("agent_type", template_name)
        return self.create_agent(name, agent_type, merged)

    def create_specialized_team(
        self,
        team_name: str,
        specializations: list[str],
        base_config: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        agents: list[dict[str, Any]] = []
        for spec in specializations:
            agent = self.create_agent(
                name=f"{team_name}_{spec}",
                agent_type=spec,
                config={**(base_config or {}), "team": team_name},
            )
            agents.append(agent)
        return agents

    def validate_creation(self, agent_data: dict[str, Any]) -> dict[str, Any]:
        errors: list[str] = []
        if not agent_data.get("name"):
            errors.append("Agent name is required")
        if not agent_data.get("type"):
            errors.append("Agent type is required")
        return {"valid": len(errors) == 0, "errors": errors}

    def get_agent(self, agent_id: str) -> dict[str, Any] | None:
        return self._created_agents.get(agent_id)

    def list_agents(self) -> list[dict[str, Any]]:
        return list(self._created_agents.values())

    def remove_agent(self, agent_id: str) -> bool:
        return self._created_agents.pop(agent_id, None) is not None

    @property
    def creation_count(self) -> int:
        return self._creation_count

    def snapshot(self) -> dict[str, Any]:
        return {
            "total_created": self._creation_count,
            "active_agents": len(self._created_agents),
        }
