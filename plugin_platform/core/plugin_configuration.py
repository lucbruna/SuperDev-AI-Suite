from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class PluginConfig(BaseModel):
    id: str
    name: str
    version: str
    entrypoint: str
    permissions: list[str] = Field(default_factory=lambda: ["filesystem.read"])
    dependencies: list[str] = Field(default_factory=list)
    settings: dict[str, Any] = Field(default_factory=dict)

    def get_setting(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default)

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()