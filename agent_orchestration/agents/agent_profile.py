"""Agent profile construction (Volume 31)."""

from __future__ import annotations

import time

from agent_orchestration.agents.agent_capabilities import AgentCapabilityRegistry
from agent_orchestration.orchestrator_models import AgentCapability, AgentProfile
from agent_orchestration.orchestrator_protocols import new_id

_STANDARD_ROLES = {
    "coding": (["code"], ["editor", "git", "test_runner"],
               ["write.project", "read.project"]),
    "testing": (["test"], ["test_runner", "coverage"], ["read.project"]),
    "security": (["security"], ["scanner", "audit"],
                 ["read.project", "audit.system"]),
    "data": (["data"], ["sql", "etl"], ["read.project", "write.data"]),
    "research": (["research"], ["search", "web"], ["read.project"]),
    "devops": (["devops"], ["docker", "ci"], ["deploy.project"]),
    "documentation": (["documentation"], ["docs", "wiki"],
                      ["read.project", "write.docs"]),
}


class AgentProfileBuilder:
    """Builds AgentProfile instances, including standard role presets."""

    def __init__(self) -> None:
        self.capabilities = AgentCapabilityRegistry()

    def build(self, name: str, objective: str = "",
              role: str = "worker",
              capabilities: list[AgentCapability] | None = None,
              tools: list[str] | None = None,
              permissions: list[str] | None = None,
              knowledge: list[str] | None = None,
              limitations: list[str] | None = None) -> AgentProfile:
        return AgentProfile(
            agent_id=new_id("agent"), name=name, objective=objective,
            role=role, capabilities=list(capabilities or []),
            tools=list(tools or []), permissions=list(permissions or []),
            knowledge=list(knowledge or []), limitations=list(limitations or []),
            created_at=time.time())

    def standard(self, role: str, name: str = "") -> AgentProfile:
        preset = _STANDARD_ROLES.get(role)
        if preset is None:
            return self.build(name or role, objective="",
                              role=role, permissions=["read.public"])
        capability_names, tools, permissions = preset
        capabilities = [capability for capability
                        in (self.capabilities.get(cap_name)
                            for cap_name in capability_names)
                        if capability is not None]
        return self.build(name or role, objective=f"executar {role}",
                          role=role, capabilities=capabilities,
                          tools=tools, permissions=permissions)
