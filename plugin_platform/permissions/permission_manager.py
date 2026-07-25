from __future__ import annotations

from typing import Any


class PermissionManager:
    def __init__(self) -> None:
        self._permissions: dict[str, dict[str, bool]] = {}
        self._requests: dict[str, list[dict[str, str]]] = {}

    def check(self, plugin_name: str, permission: str) -> bool:
        plugin_perms = self._permissions.get(plugin_name, {})
        return plugin_perms.get(permission, False)

    def request_permission(self, plugin_name: str, permission: str, reason: str) -> bool:
        self._requests.setdefault(plugin_name, []).append({
            "permission": permission,
            "reason": reason,
            "status": "pending",
        })
        return self.check(plugin_name, permission)

    def grant(self, plugin_name: str, permission: str) -> None:
        if plugin_name not in self._permissions:
            self._permissions[plugin_name] = {}
        self._permissions[plugin_name][permission] = True

        if plugin_name in self._requests:
            for req in self._requests[plugin_name]:
                if req["permission"] == permission:
                    req["status"] = "granted"

    def revoke(self, plugin_name: str, permission: str) -> None:
        if plugin_name in self._permissions:
            self._permissions[plugin_name].pop(permission, None)

        if plugin_name in self._requests:
            for req in self._requests[plugin_name]:
                if req["permission"] == permission:
                    req["status"] = "revoked"

    def get_permissions(self, plugin_name: str) -> dict[str, bool]:
        return self._permissions.get(plugin_name, {}).copy()

    def get_pending_requests(self, plugin_name: str | None = None) -> list[dict[str, Any]]:
        if plugin_name:
            return [r for r in self._requests.get(plugin_name, []) if r["status"] == "pending"]
        result = []
        for name, reqs in self._requests.items():
            for r in reqs:
                if r["status"] == "pending":
                    result.append({"plugin": name, **r})
        return result