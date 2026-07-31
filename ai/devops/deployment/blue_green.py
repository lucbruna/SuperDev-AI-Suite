"""Blue-Green deployment."""
from __future__ import annotations

from typing import Any


class BlueGreenDeployer:
    def __init__(self) -> None:
        self._environments: dict[str, dict[str, Any]] = {}
    def setup(self, name: str, blue_version: str, green_version: str) -> dict[str, Any]:
        env = {"name": name, "blue": {"version": blue_version, "active": True}, "green": {"version": green_version, "active": False}}
        self._environments[name] = env
        return env
    def switch(self, name: str) -> dict[str, Any]:
        if name not in self._environments:
            return {"error": "not_found"}
        env = self._environments[name]
        env["blue"]["active"], env["green"]["active"] = env["green"]["active"], env["blue"]["active"]
        return env
    def get_status(self, name: str) -> dict[str, Any]:
        return self._environments.get(name, {"error": "not_found"})
    def list_all(self) -> list[dict[str, Any]]:
        return list(self._environments.values())
    def count(self) -> int:
        return len(self._environments)
