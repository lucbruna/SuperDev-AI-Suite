from __future__ import annotations

from typing import Any

from .tool_interfaces import ITool


class ToolRepository:
    """Persistent storage and retrieval of tool configurations."""

    def __init__(self) -> None:
        self._configs: dict[str, dict[str, Any]] = {}
        self._tool_metadata: dict[str, dict[str, Any]] = {}

    def save_config(self, tool_name: str, config: dict[str, Any]) -> str:
        self._configs[tool_name] = config
        return tool_name

    def get_config(self, tool_name: str) -> dict[str, Any] | None:
        return self._configs.get(tool_name)

    def delete_config(self, tool_name: str) -> bool:
        if tool_name in self._configs:
            del self._configs[tool_name]
            return True
        return False

    def list_configs(self) -> list[str]:
        return list(self._configs.keys())

    def save_metadata(self, tool_name: str, metadata: dict[str, Any]) -> str:
        self._tool_metadata[tool_name] = metadata
        return tool_name

    def get_metadata(self, tool_name: str) -> dict[str, Any] | None:
        return self._tool_metadata.get(tool_name)

    @property
    def config_count(self) -> int:
        return len(self._configs)

    def to_dict(self) -> dict[str, Any]:
        return {
            "config_count": self.config_count,
            "tools": list(self._configs.keys()),
        }
