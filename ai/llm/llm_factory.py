from __future__ import annotations

from typing import Any

from .llm_interfaces import ILLMFactory, ILLMProvider


class LLMFactory(ILLMFactory):
    """Creates LLM provider instances by type name."""

    def __init__(self) -> None:
        self._provider_classes: dict[str, type[ILLMProvider]] = {}

    def register_class(self, provider_type: str, cls: type[ILLMProvider]) -> str:
        self._provider_classes[provider_type] = cls
        return provider_type

    def create(self, provider_type: str, **kwargs: Any) -> ILLMProvider:
        cls = self._provider_classes.get(provider_type)
        if cls is None:
            raise ValueError(f"Unknown provider type: {provider_type}")
        return cls(**kwargs)

    def list_types(self) -> list[str]:
        return list(self._provider_classes.keys())

    @property
    def type_count(self) -> int:
        return len(self._provider_classes)

    def to_dict(self) -> dict[str, Any]:
        return {
            "types": list(self._provider_classes.keys()),
            "type_count": self.type_count,
        }
