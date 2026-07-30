from __future__ import annotations

from typing import Any, Callable

from .ai_config import AIConfig, get_ai_config
from .ai_types import ProviderType


class AIFactory:
    """Factory for creating AI engine instances."""

    def __init__(self):
        self._builders: dict[str, Callable[..., Any]] = {}

    def register_builder(self, key: str, builder: Callable[..., Any]) -> None:
        """Register a custom builder function."""
        self._builders[key] = builder

    def create_engine(self, config: AIConfig | None = None) -> Any:
        """Create an AI engine instance."""
        from .ai_engine import AIEngine

        return AIEngine(config or get_ai_config())

    def create_provider(self, provider_type: ProviderType | str, **kwargs: Any) -> Any:
        """Create a provider instance."""
        if provider_type in self._builders:
            return self._builders[provider_type](**kwargs)

        provider_map = {
            "openai": "ai.providers.openai.openai_provider.OpenAIProvider",
            "anthropic": "ai.providers.anthropic.anthropic_provider.AnthropicProvider",
            "gemini": "ai.providers.gemini",
            "ollama": "ai.providers.ollama.ollama_provider.OllamaProvider",
            "openrouter": "ai.providers.openrouter.openrouter_provider.OpenRouterProvider",
        }
        import_path = provider_map.get(provider_type)
        if not import_path:
            msg = f"Unknown provider type: {provider_type}"
            raise ValueError(msg)

        # Lazy import
        module_path, class_name = import_path.rsplit(".", 1)
        import importlib

        module = importlib.import_module(module_path)
        cls = getattr(module, class_name)
        return cls(**kwargs)

    def create_agent(self, agent_type: str = "generic", **kwargs: Any) -> Any:
        """Create an agent instance."""
        if agent_type in self._builders:
            return self._builders[agent_type](**kwargs)

        from .core.agent_system import AgentSystem

        return AgentSystem(**kwargs)

    def create_router(self, router_type: str = "default", **kwargs: Any) -> Any:
        """Create a router instance."""
        if router_type in self._builders:
            return self._builders[router_type](**kwargs)

        from .routing.router import AIRouter

        return AIRouter(**kwargs)

    def list_builders(self) -> list[str]:
        """List all registered custom builders."""
        return list(self._builders.keys())
