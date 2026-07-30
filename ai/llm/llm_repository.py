from __future__ import annotations

from typing import Any

from dataclasses import asdict

from .llm_registry import LLMRegistry


class LLMRepository:
    """Repository for LLM provider configurations and metadata."""

    def __init__(self, registry: LLMRegistry) -> None:
        self._registry = registry
        self._configs: dict[str, dict[str, Any]] = {}
        self._metadata: dict[str, dict[str, Any]] = {}

    def save_config(self, provider: str, config: dict[str, Any]) -> None:
        self._configs[provider] = config

    def get_config(self, provider: str) -> dict[str, Any] | None:
        return self._configs.get(provider)

    def save_metadata(self, provider: str, metadata: dict[str, Any]) -> None:
        self._metadata[provider] = metadata

    def get_metadata(self, provider: str) -> dict[str, Any] | None:
        return self._metadata.get(provider)

    def list_providers_with_configs(self) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        for name in self._registry.list_names():
            info = self._registry.get_info(name)
            config = self._configs.get(name, {})
            metadata = self._metadata.get(name, {})
            result.append({
                "name": name,
                "info": asdict(info) if info else {},
                "config": config,
                "metadata": metadata,
            })
        return result

    def to_dict(self) -> dict[str, Any]:
        return {
            "configured_providers": list(self._configs.keys()),
            "provider_count": len(self._configs),
        }
