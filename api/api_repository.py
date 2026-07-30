from __future__ import annotations

from typing import Any

from .api_registry import APIRegistry


class APIRepository:
    """Data repository for API configurations and state."""

    def __init__(self, registry: APIRegistry) -> None:
        self._registry = registry
        self._configs: dict[str, dict[str, Any]] = {}
        self._state: dict[str, Any] = {}

    def save_config(self, key: str, config: dict[str, Any]) -> None:
        self._configs[key] = config

    def get_config(self, key: str) -> dict[str, Any] | None:
        return self._configs.get(key)

    def set_state(self, key: str, value: Any) -> None:
        self._state[key] = value

    def get_state(self, key: str, default: Any = None) -> Any:
        return self._state.get(key, default)

    def list_configs(self) -> list[str]:
        return list(self._configs.keys())

    def to_dict(self) -> dict[str, Any]:
        return {"config_count": len(self._configs), "state_keys": list(self._state.keys())}
