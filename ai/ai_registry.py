from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .ai_constants import DEFAULT_MODELS, PROVIDER_NAMES
from .ai_exceptions import RegistryError


class AIRegistry:
    """Central registry for agents, tools, and models."""

    def __init__(self):
        self._agents: dict[str, Any] = {}
        self._tools: dict[str, Any] = {}
        self._models: dict[str, dict[str, Any]] = {}
        self._initialized = False

    def initialize(self) -> None:
        """Initialize registry with default models."""
        if self._initialized:
            return
        for provider, model in DEFAULT_MODELS.items():
            self._models[model] = {
                "name": model,
                "provider": provider,
                "is_default": True,
                "registered_at": datetime.now(UTC).isoformat(),
            }
        self._initialized = True

    def register_agent(self, name: str, agent: Any) -> None:
        """Register an agent by name."""
        if name in self._agents:
            raise RegistryError(f"Agent '{name}' is already registered")
        self._agents[name] = agent

    def register_tool(self, name: str, tool: Any) -> None:
        """Register a tool by name."""
        if name in self._tools:
            raise RegistryError(f"Tool '{name}' is already registered")
        self._tools[name] = tool

    def register_model(self, name: str, model_config: dict[str, Any]) -> None:
        """Register a model configuration."""
        self._models[name] = {**model_config, "registered_at": datetime.now(UTC).isoformat()}

    def get_agent(self, name: str) -> Any | None:
        """Get a registered agent by name."""
        return self._agents.get(name)

    def get_tool(self, name: str) -> Any | None:
        """Get a registered tool by name."""
        return self._tools.get(name)

    def get_model(self, name: str) -> dict[str, Any] | None:
        """Get a registered model configuration."""
        return self._models.get(name)

    def unregister_agent(self, name: str) -> None:
        """Unregister an agent."""
        self._agents.pop(name, None)

    def unregister_tool(self, name: str) -> None:
        """Unregister a tool."""
        self._tools.pop(name, None)

    def list_agents(self) -> list[str]:
        """List all registered agent names."""
        return list(self._agents.keys())

    def list_tools(self) -> list[str]:
        """List all registered tool names."""
        return list(self._tools.keys())

    def list_models(self) -> list[dict[str, Any]]:
        """List all registered models with their configs."""
        return [
            {"name": name, **config}
            for name, config in self._models.items()
        ]

    def get_models_by_provider(self, provider: str) -> list[dict[str, Any]]:
        """Get all models for a specific provider."""
        return [
            {"name": name, **config}
            for name, config in self._models.items()
            if config.get("provider") == provider
        ]

    def health(self) -> dict[str, Any]:
        """Get registry health status."""
        return {
            "status": "healthy",
            "agents": len(self._agents),
            "tools": len(self._tools),
            "models": len(self._models),
            "initialized": self._initialized,
            "timestamp": datetime.now(UTC).isoformat(),
        }
