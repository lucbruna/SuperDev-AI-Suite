"""Agent versioning and upgrade management."""
from __future__ import annotations

import time
from typing import Any


class VersionManager:
    """Manages agent versioning, migrations, and upgrades."""

    def __init__(self) -> None:
        self._versions: dict[str, list[dict[str, Any]]] = {}
        self._current: dict[str, str] = {}

    def register_version(self, agent_id: str, version: str,
                         changelog: str = "",
                         metadata: dict[str, Any] | None = None) -> None:
        self._versions.setdefault(agent_id, []).append({
            "version": version,
            "changelog": changelog,
            "metadata": metadata or {},
            "registered_at": time.time(),
        })
        self._current[agent_id] = version

    def get_current_version(self, agent_id: str) -> str | None:
        return self._current.get(agent_id)

    def get_version_history(self, agent_id: str) -> list[dict[str, Any]]:
        return list(self._versions.get(agent_id, []))

    def upgrade(self, agent_id: str, new_version: str,
                changelog: str = "") -> dict[str, Any]:
        old = self._current.get(agent_id, "0.0.0")
        self.register_version(agent_id, new_version, changelog)
        return {
            "agent_id": agent_id,
            "from": old,
            "to": new_version,
            "status": "upgraded",
        }

    def rollback(self, agent_id: str) -> dict[str, Any]:
        history = self._versions.get(agent_id, [])
        if len(history) < 2:
            return {"agent_id": agent_id, "status": "error", "error": "No previous version"}
        prev = history[-2]["version"]
        self._current[agent_id] = prev
        return {"agent_id": agent_id, "status": "rolled_back", "to": prev}

    def snapshot(self) -> dict[str, Any]:
        return {
            "agents": len(self._versions),
            "current": dict(self._current),
        }
