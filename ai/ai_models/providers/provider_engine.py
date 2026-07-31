"""Provider engine."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


class ProviderEngine:
    def __init__(self) -> None:
        self._providers: dict[str, Callable] = {}
        self._configs: dict[str, dict[str, Any]] = {}
        self._started = False

    def start(self) -> None:
        self._started = True

    def register(self, name: str, handler: Callable, config: dict[str, Any] = None) -> None:
        self._providers[name] = handler
        self._configs[name] = config or {}

    def unregister(self, name: str) -> bool:
        if name in self._providers:
            del self._providers[name]
            self._configs.pop(name, None)
            return True
        return False

    def complete(self, provider_name: str, prompt: str, **kwargs: Any) -> dict[str, Any]:
        handler = self._providers.get(provider_name)
        if not handler:
            return {"error": "provider_not_found", "status": "failed"}
        try:
            return handler(prompt, **kwargs)
        except Exception as e:
            return {"error": str(e), "status": "failed"}

    def list_providers(self) -> list[str]:
        return list(self._providers.keys())

    def is_registered(self, name: str) -> bool:
        return name in self._providers

    def get_config(self, name: str) -> dict[str, Any]:
        return self._configs.get(name, {})

    def count(self) -> int:
        return len(self._providers)

    def is_running(self) -> bool:
        return self._started
