"""DirectorAgent: orchestrates the agent swarm by capability routing."""
from __future__ import annotations

from typing import Any

from aios.agents.base_agent import BaseAgent


class DirectorAgent(BaseAgent):
    """Delegates work to the most suitable agent for each requested capability."""

    def __init__(self, name: str = "director", registry: Any = None, **kwargs: Any) -> None:
        super().__init__(
            name=name,
            role="director",
            capabilities=["orchestration", "delegation", "coordination"],
            description="Coordinates the agent swarm",
            **kwargs,
        )
        self.registry = registry

    def process(self, input_data: Any, context: dict[str, Any]) -> Any:
        goal = input_data if isinstance(input_data, str) else str(input_data.get("goal", ""))
        if isinstance(input_data, dict):
            requested = list(input_data.get("capabilities", []))
        else:
            requested = list(context.get("capabilities", []))
        delegation = []
        for capability in requested:
            agent_name = "unassigned"
            if self.registry is not None:
                matches = self.registry.find_by_capability(capability)
                if matches:
                    agent_name = matches[0].name
            delegation.append({"capability": capability, "agent": agent_name})
        return {
            "goal": goal,
            "delegation": delegation,
            "summary": f"directed {len(delegation)} task(s) for goal {goal!r}",
            "total_agents": len(self.registry.agents()) if self.registry is not None else 0,
        }
