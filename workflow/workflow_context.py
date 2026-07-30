from __future__ import annotations

from typing import Any


class WorkflowContext:
    """Execution context for a workflow instance."""

    def __init__(self, workflow_id: str) -> None:
        self._workflow_id = workflow_id
        self._variables: dict[str, Any] = {}
        self._metadata: dict[str, str] = {}

    @property
    def workflow_id(self) -> str:
        return self._workflow_id

    def set(self, key: str, value: Any) -> None:
        self._variables[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._variables.get(key, default)

    def set_meta(self, key: str, value: str) -> None:
        self._metadata[key] = value

    def get_meta(self, key: str, default: str = "") -> str:
        return self._metadata.get(key, default)

    def snapshot(self) -> dict[str, Any]:
        return {
            "workflow_id": self._workflow_id,
            "variables": dict(self._variables),
            "metadata": dict(self._metadata),
        }
