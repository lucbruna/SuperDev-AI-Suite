"""Enterprise Memory — long-lived fact store for the studio."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration.enterprise_ai.memory_connector import (
    get_memory_connector,
)


class EnterpriseMemory:
    """Namespaced fact memory (persistable via export)."""

    def __init__(self) -> None:
        self._namespaces: dict[str, dict[str, Any]] = {}

    def remember(self, namespace: str, key: str, value: Any) -> dict[str, Any]:
        self._namespaces.setdefault(namespace, {})[key] = value
        get_memory_connector().store(f"{namespace}:{key}={value}", kind="enterprise_memory")
        return {"namespace": namespace, "remembered": len(self._namespaces.get(namespace, {}))}

    def recall(self, namespace: str, key: str | None = None) -> dict[str, Any]:
        ns = self._namespaces.get(namespace, {})
        if key is not None:
            return {"namespace": namespace, "key": key, "value": ns.get(key)}
        return {"namespace": namespace, "values": dict(ns)}

    def snapshot(self) -> dict[str, Any]:
        return {"namespaces": {n: dict(v) for n, v in self._namespaces.items()}}


_enterprise_memory: EnterpriseMemory | None = None


def get_enterprise_memory() -> EnterpriseMemory:
    global _enterprise_memory
    if _enterprise_memory is None:
        _enterprise_memory = EnterpriseMemory()
    return _enterprise_memory
