"""Configuration for the Knowledge Graph & Enterprise Memory Engine."""

from __future__ import annotations

from typing import Any

_DEFAULTS = {
    "entity_prefix": "@",
    "max_memory_items": 1000,
    "max_graph_nodes": 10000,
    "search_default_limit": 20,
    "embedding_dimensions": 32,
    "retention_default_days": 365,
    "log_level": "INFO",
}


class EnterpriseKnowledgeConfig:
    """Typed access over a merged settings dictionary."""

    def __init__(self, **values: Any) -> None:
        self._values = dict(_DEFAULTS)
        self._values.update(values)

    @classmethod
    def defaults(cls) -> dict[str, Any]:
        return dict(_DEFAULTS)

    def get(self, key: str, default: Any = None) -> Any:
        return self._values.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._values[key] = value

    def update(self, **overrides: Any) -> "EnterpriseKnowledgeConfig":
        self._values.update(overrides)
        return self

    def merge(self, other: dict[str, Any] | None) -> "EnterpriseKnowledgeConfig":
        if other:
            self._values.update(other)
        return self

    def to_dict(self) -> dict[str, Any]:
        return dict(self._values)

    def __getattr__(self, name: str) -> Any:
        try:
            return self._values[name]
        except KeyError as exc:
            raise AttributeError(f"no config key '{name}'") from exc
