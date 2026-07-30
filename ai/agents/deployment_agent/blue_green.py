from __future__ import annotations

from typing import Any


class BlueGreen:
    """Manages blue-green deployment strategy."""

    def __init__(self) -> None:
        self._active: str = "blue"
        self._environments: dict[str, dict[str, Any]] = {"blue": {}, "green": {}}

    def set_active(self, env: str) -> bool:
        if env in self._environments:
            self._active = env
            return True
        return False

    def get_active(self) -> str:
        return self._active

    def deploy(self, env: str, config: dict[str, Any]) -> str:
        if env in self._environments:
            self._environments[env] = config
            return env
        return ""

    def switch(self) -> dict[str, Any]:
        old = self._active
        new = "green" if self._active == "blue" else "blue"
        self._active = new
        return {"old": old, "new": new}

    def to_dict(self) -> dict[str, Any]:
        return {
            "active": self._active,
            "environments": {k: v for k, v in self._environments.items()},
        }
