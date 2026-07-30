from __future__ import annotations

from typing import Any


class ExecutionContext:
    """Context data passed through workflow execution."""

    def __init__(self, workflow_id: str = "") -> None:
        self._workflow_id = workflow_id
        self._variables: dict[str, Any] = {}
        self._secrets: dict[str, str] = {}
        self._artifacts: dict[str, str] = {}

    @property
    def workflow_id(self) -> str:
        return self._workflow_id

    def set(self, key: str, value: Any) -> None:
        self._variables[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._variables.get(key, default)

    def set_secret(self, key: str, value: str) -> None:
        self._secrets[key] = value

    def get_secret(self, key: str) -> str | None:
        return self._secrets.get(key)

    def add_artifact(self, name: str, path: str) -> None:
        self._artifacts[name] = path

    def snapshot(self) -> dict[str, Any]:
        return {
            "workflow_id": self._workflow_id,
            "variables": dict(self._variables),
            "artifacts": dict(self._artifacts),
        }
