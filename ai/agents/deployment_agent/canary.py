from __future__ import annotations

from typing import Any


class Canary:
    """Manages canary deployment strategy."""

    def __init__(self) -> None:
        self._config: dict[str, Any] = {"percentage": 0, "duration": 0}
        self._history: list[dict[str, Any]] = []

    def configure(self, percentage: int, duration: int) -> str:
        self._config = {"percentage": percentage, "duration": duration}
        return "configured"

    def get_config(self) -> dict[str, Any]:
        return dict(self._config)

    def promote(self) -> str:
        self._history.append({"action": "promote", "config": dict(self._config)})
        self._config["percentage"] = 100
        return "promoted"

    def rollback(self) -> str:
        self._history.append({"action": "rollback", "config": dict(self._config)})
        self._config["percentage"] = 0
        return "rolled_back"

    def to_dict(self) -> dict[str, Any]:
        return {
            "config": dict(self._config),
            "history": self._history,
        }
