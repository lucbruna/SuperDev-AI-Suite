"""AIOS Configuration Service — layered settings.

Settings resolve from: defaults < loaded dicts < environment variables
(prefix "AIOS_") < runtime overrides. Deterministic and flat at read.
"""

from __future__ import annotations

import os
from typing import Any


def _dig(settings: dict[str, Any], key: str, default: Any = None) -> Any:
    current: Any = settings
    for part in key.split("."):
        if not isinstance(current, dict) or part not in current:
            return default
        current = current[part]
    return current


class ConfigurationService:
    """Layered configuration with dotted-key access."""

    def __init__(self, defaults: dict[str, Any] | None = None, env_prefix: str = "AIOS_") -> None:
        self._env_prefix = env_prefix
        self._layers: list[dict[str, Any]] = [dict(defaults or {})]
        self._overrides: dict[str, Any] = {}

    def load(self, settings: dict[str, Any]) -> "ConfigurationService":
        self._layers.append(dict(settings))
        return self

    def set(self, key: str, value: Any) -> None:
        self._overrides[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        for layer in reversed(self._layers):
            value = _dig(layer, key, None)
            if value is not None:
                return value
        env_key = self._env_prefix + key.upper().replace(".", "_")
        if env_key in os.environ:
            return os.environ[env_key]
        return self._overrides.get(key, default)

    def all(self) -> dict[str, Any]:
        merged: dict[str, Any] = {}
        for layer in self._layers:
            merged.update(layer)
        merged.update(self._overrides)
        return merged

    def snapshot(self) -> dict[str, Any]:
        return {"layers": len(self._layers), "keys": sorted(self.all())}
