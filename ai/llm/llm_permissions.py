from __future__ import annotations

from typing import Any


class LLMPermissions:
    """Manages permissions for LLM operations."""

    def __init__(self) -> None:
        self._provider_permissions: dict[str, list[str]] = {}
        self._model_permissions: dict[str, list[str]] = {}

    def grant_provider(self, provider: str, permission: str) -> None:
        if provider not in self._provider_permissions:
            self._provider_permissions[provider] = []
        self._provider_permissions[provider].append(permission)

    def grant_model(self, model: str, permission: str) -> None:
        if model not in self._model_permissions:
            self._model_permissions[model] = []
        self._model_permissions[model].append(permission)

    def can_access_provider(self, provider: str, permission: str = "use") -> bool:
        perms = self._provider_permissions.get(provider, [])
        return "all" in perms or permission in perms

    def can_access_model(self, model: str, permission: str = "use") -> bool:
        perms = self._model_permissions.get(model, [])
        return "all" in perms or permission in perms

    def revoke_provider(self, provider: str, permission: str | None = None) -> None:
        if permission:
            perms = self._provider_permissions.get(provider, [])
            if permission in perms:
                perms.remove(permission)
        else:
            self._provider_permissions.pop(provider, None)

    def revoke_model(self, model: str, permission: str | None = None) -> None:
        if permission:
            perms = self._model_permissions.get(model, [])
            if permission in perms:
                perms.remove(permission)
        else:
            self._model_permissions.pop(model, None)

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_permissions": dict(self._provider_permissions),
            "model_permissions": dict(self._model_permissions),
        }
