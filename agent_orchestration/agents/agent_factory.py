"""Standard agent factory (Volume 31)."""

from __future__ import annotations

from agent_orchestration.agents.agent_profile import AgentProfileBuilder
from agent_orchestration.orchestrator_models import AgentProfile

_TEAM_ROLES = ["coding", "testing", "security", "data", "devops",
               "documentation"]


class AgentFactory:
    """Creates standard role agents and teams."""

    def __init__(self, builder: AgentProfileBuilder | None = None) -> None:
        self.builder = builder or AgentProfileBuilder()

    def create(self, role: str, name: str = "") -> AgentProfile:
        return self.builder.standard(role, name)

    def create_team(self, roles: list[str]) -> list[AgentProfile]:
        return [self.create(role) for role in roles]

    def create_coding_team(self) -> list[AgentProfile]:
        return self.create_team(_TEAM_ROLES)
