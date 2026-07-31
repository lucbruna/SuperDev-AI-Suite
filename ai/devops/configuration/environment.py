"""Environment manager."""
from __future__ import annotations
from typing import Any, Dict, List

class EnvironmentManager:
    def __init__(self) -> None:
        self._environments: Dict[str, Dict[str, Any]] = {}
    def create(self, name: str, variables: Dict[str, str] = None) -> Dict[str, Any]:
        env = {"name": name, "variables": variables or {}, "status": "active"}
        self._environments[name] = env
        return env
    def set_variable(self, env_name: str, key: str, value: str) -> bool:
        if env_name not in self._environments:
            return False
        self._environments[env_name]["variables"][key] = value
        return True
    def get_variable(self, env_name: str, key: str) -> str:
        return self._environments.get(env_name, {}).get("variables", {}).get(key, "")
    def get_all(self, env_name: str) -> Dict[str, str]:
        return self._environments.get(env_name, {}).get("variables", {})
    def list_environments(self) -> List[str]:
        return list(self._environments.keys())
    def delete(self, name: str) -> bool:
        if name in self._environments:
            del self._environments[name]
            return True
        return False
    def count(self) -> int:
        return len(self._environments)
