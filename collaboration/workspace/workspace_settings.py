"""Workspace settings management."""

from __future__ import annotations

from typing import Any

DEFAULTS: dict[str, Any] = {
    "timezone": "America/Sao_Paulo",
    "default_role": "developer",
    "allow_agents": True,
    "require_review": True,
    "require_approval": True,
    "audit_enabled": True,
}


class WorkspaceSettings:
    """Per-workspace configuration with defaults and validation."""

    def __init__(self, workspace_id: str,
                 initial: dict[str, Any] | None = None) -> None:
        self.workspace_id = workspace_id
        self._values: dict[str, Any] = dict(DEFAULTS)
        self._values.update(initial or {})

    def get(self, key: str, default: Any = None) -> Any:
        return self._values.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._values[key] = value

    def update(self, **overrides: Any) -> None:
        self._values.update(overrides)

    def to_dict(self) -> dict[str, Any]:
        return {"workspace_id": self.workspace_id,
                "settings": dict(self._values)}

    @staticmethod
    def validate(values: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        timezone = values.get("timezone")
        if timezone and "/" not in str(timezone) and str(timezone) != "UTC":
            errors.append("timezone deve seguir o formato Area/Cidade")
        return errors
