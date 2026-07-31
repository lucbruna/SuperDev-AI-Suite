"""Identity provider management (OAuth, LDAP, etc.)."""

from __future__ import annotations

from typing import Any


class IdentityProviderManager:
    def __init__(self) -> None:
        self._providers: dict[str, dict[str, Any]] = {}

    def register(self, name: str, provider_type: str, config: dict[str, Any]) -> dict[str, Any]:
        self._providers[name] = {"name": name, "type": provider_type, "config": config, "enabled": True}
        return {"status": "registered", "name": name}

    def get(self, name: str) -> dict[str, Any] | None:
        return dict(self._providers[name]) if name in self._providers else None

    def list_all(self) -> list[dict[str, Any]]:
        return [{"name": p["name"], "type": p["type"]} for p in self._providers.values()]

    def count(self) -> int:
        return len(self._providers)
