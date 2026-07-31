"""Capability catalog for agents (Volume 31)."""

from __future__ import annotations

from agent_orchestration.orchestrator_models import AgentCapability


class AgentCapabilityRegistry:
    """Registry of known agent capabilities."""

    def __init__(self) -> None:
        self._capabilities: dict[str, AgentCapability] = {}
        self._seed()

    def _seed(self) -> None:
        self.register("code", "criar código", ["editor", "git", "test_runner"])
        self.register("test", "executar testes", ["test_runner", "coverage"])
        self.register("security", "verificar segurança", ["scanner", "audit"])
        self.register("data", "modelar e consultar dados", ["sql", "etl"])
        self.register("research", "pesquisar informação", ["search", "web"])
        self.register("devops", "implantar e operar", ["docker", "ci"])
        self.register("documentation", "escrever documentação",
                      ["docs", "wiki"])

    def register(self, name: str, description: str = "",
                 tools: list[str] | None = None,
                 max_load: int = 1) -> AgentCapability:
        capability = AgentCapability(name=name, description=description,
                                     tools=list(tools or []),
                                     max_load=max_load)
        self._capabilities[name] = capability
        return capability

    def get(self, name: str) -> AgentCapability | None:
        return self._capabilities.get(name)

    def all(self) -> list[AgentCapability]:
        return list(self._capabilities.values())

    def names(self) -> list[str]:
        return list(self._capabilities)
