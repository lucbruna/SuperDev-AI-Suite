from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PluginStatus(StrEnum):
    INSTALLED = "installed"
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"
    UPDATING = "updating"


class PluginType(StrEnum):
    EXTENSION = "extension"
    INTEGRATION = "integration"
    TOOL = "tool"
    PROVIDER = "provider"
    UI = "ui"
    COMMAND = "command"


@dataclass
class PluginMetadata:
    name: str
    slug: str
    version: str
    description: str = ""
    author: str = ""
    author_email: str = ""
    homepage: str = ""
    repository: str = ""
    license: str = "MIT"
    plugin_type: PluginType = PluginType.EXTENSION
    tags: list[str] = field(default_factory=list)
    min_platform_version: str = "5.0.0"
    max_platform_version: str | None = None
    dependencies: list[str] = field(default_factory=list)
    config_schema: dict[str, Any] = field(default_factory=dict)
    icon_url: str | None = None


@dataclass
class PluginConfig:
    enabled: bool = True
    settings: dict[str, Any] = field(default_factory=dict)


class BasePlugin(ABC):
    """Abstract base class for SuperDev plugins."""

    def __init__(self, metadata: PluginMetadata, config: PluginConfig | None = None):
        self.metadata = metadata
        self.config = config or PluginConfig()
        self._status = PluginStatus.INSTALLED
        self._hooks: dict[str, list] = {}

    @property
    def status(self) -> PluginStatus:
        return self._status

    @property
    def name(self) -> str:
        return self.metadata.name

    @property
    def slug(self) -> str:
        return self.metadata.slug

    @property
    def version(self) -> str:
        return self.metadata.version

    async def activate(self) -> None:
        self._status = PluginStatus.ENABLED
        await self.on_activate()

    async def deactivate(self) -> None:
        self._status = PluginStatus.DISABLED
        await self.on_deactivate()

    @abstractmethod
    async def on_activate(self) -> None:
        ...

    @abstractmethod
    async def on_deactivate(self) -> None:
        ...

    async def on_config_change(self, config: dict[str, Any]) -> None:
        self.config.settings.update(config)

    def register_hook(self, hook_name: str, handler) -> None:
        if hook_name not in self._hooks:
            self._hooks[hook_name] = []
        self._hooks[hook_name].append(handler)

    async def trigger_hook(self, hook_name: str, **kwargs) -> list[Any]:
        results = []
        for handler in self._hooks.get(hook_name, []):
            try:
                result = await handler(**kwargs) if callable(handler) else handler
                results.append(result)
            except Exception as e:
                results.append({"error": str(e)})
        return results

    def get_api(self) -> dict[str, Any]:
        return {
            "name": self.metadata.name,
            "slug": self.metadata.slug,
            "version": self.metadata.version,
            "status": self._status.value,
            "config": self.config.settings,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "metadata": {
                "name": self.metadata.name,
                "slug": self.metadata.slug,
                "version": self.metadata.version,
                "description": self.metadata.description,
                "author": self.metadata.author,
                "plugin_type": self.metadata.plugin_type.value,
                "tags": self.metadata.tags,
                "dependencies": self.metadata.dependencies,
            },
            "status": self._status.value,
            "config": self.config.settings,
        }
