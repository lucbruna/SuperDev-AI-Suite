"""Load agents from configuration dicts (Volume 31)."""

from __future__ import annotations

from agent_orchestration.agents.agent_capabilities import AgentCapabilityRegistry
from agent_orchestration.agents.agent_profile import AgentProfileBuilder
from agent_orchestration.orchestrator_models import AgentProfile


class AgentLoader:
    """Builds AgentProfile lists from plain dict definitions."""

    def __init__(self) -> None:
        self.capabilities = AgentCapabilityRegistry()
        self.builder = AgentProfileBuilder()

    def _from_entry(self, entry: dict) -> AgentProfile:
        capability_names = entry.get("capabilities", [])
        capabilities = [capability for capability
                        in (self.capabilities.get(name)
                            for name in capability_names)
                        if capability is not None]
        return self.builder.build(
            name=entry["name"], objective=entry.get("objective", ""),
            role=entry.get("role", "worker"), capabilities=capabilities,
            tools=entry.get("tools", []), permissions=entry.get(
                "permissions", []), knowledge=entry.get("knowledge", []),
            limitations=entry.get("limitations", []))

    def load_from_dict(self, data: dict) -> list[AgentProfile]:
        return self.load_from_list(data.get("agents", []))

    def load_from_list(self, items: list[dict]) -> list[AgentProfile]:
        return [self._from_entry(item) for item in items]
