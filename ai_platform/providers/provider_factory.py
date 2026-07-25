from __future__ import annotations
from typing import Optional
from .base_provider import BaseProvider
from .provider_configuration import ProviderConfig
from .openai.openai_provider import OpenAIProvider
from .anthropic.anthropic_provider import AnthropicProvider
from .gemini.gemini_provider import GeminiProvider
from .ollama.ollama_provider import OllamaProvider
from .openrouter.openrouter_provider import OpenRouterProvider


class ProviderFactory:
    _type_map: dict[str, type[BaseProvider]] = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "gemini": GeminiProvider,
        "ollama": OllamaProvider,
        "openrouter": OpenRouterProvider,
    }

    @classmethod
    def register_type(cls, type_name: str, provider_class: type[BaseProvider]) -> None:
        cls._type_map[type_name] = provider_class

    @classmethod
    def create(cls, config: ProviderConfig) -> BaseProvider:
        provider_class = cls._type_map.get(config.type)
        if provider_class is None:
            raise ValueError(f"Unknown provider type: {config.type}. Supported: {list(cls._type_map.keys())}")
        return provider_class(config)
