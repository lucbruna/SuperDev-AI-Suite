"""
Agent Version Manager - Manages agent versions
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from enterprise_ai_core.models import Agent


class AgentVersionManager:
    """Manages agent versions and upgrades"""

    def __init__(self):
        self._versions: Dict[str, List[Dict[str, Any]]] = {}
        self._current: Dict[str, str] = {}

    def register_version(self, agent_name: str, version: str, metadata: Dict[str, Any]) -> None:
        if agent_name not in self._versions:
            self._versions[agent_name] = []

        self._versions[agent_name].append({
            "version": version,
            "metadata": metadata,
            "registered_at": datetime.utcnow(),
            "active": False,
        })

    def set_active(self, agent_name: str, version: str) -> bool:
        versions = self._versions.get(agent_name, [])
        for v in versions:
            v["active"] = v["version"] == version

        if any(v["version"] == version for v in versions):
            self._current[agent_name] = version
            return True
        return False

    def get_current(self, agent_name: str) -> Optional[str]:
        return self._current.get(agent_name)

    def get_versions(self, agent_name: str) -> List[Dict[str, Any]]:
        return self._versions.get(agent_name, [])

    def get_latest(self, agent_name: str) -> Optional[str]:
        versions = self._versions.get(agent_name, [])
        if not versions:
            return None
        return max(versions, key=lambda v: v["version"])["version"]

    def compare(self, agent_name: str, version_a: str, version_b: str) -> Dict[str, Any]:
        versions = {v["version"]: v["metadata"] for v in self._versions.get(agent_name, [])}
        return {
            "version_a": versions.get(version_a, {}),
            "version_b": versions.get(version_b, {}),
            "diff": self._diff(versions.get(version_a, {}), versions.get(version_b, {})),
        }

    def _diff(self, a: Dict, b: Dict) -> Dict[str, Any]:
        all_keys = set(a.keys()) | set(b.keys())
        return {
            k: {"old": a.get(k), "new": b.get(k)}
            for k in all_keys
            if a.get(k) != b.get(k)
        }