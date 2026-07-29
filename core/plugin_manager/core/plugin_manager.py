import logging
from typing import Optional

from .plugin_configuration import PluginConfig
from ..loader.plugin_loader import PluginModule

logger = logging.getLogger(__name__)


class PluginManager:
    def __init__(self):
        self._plugins: dict[str, PluginModule] = {}
        self._statuses: dict[str, str] = {}
        self._configs: dict[str, PluginConfig] = {}

    def register(self, module: PluginModule, config: PluginConfig) -> None:
        self._plugins[config.name] = module
        self._configs[config.name] = config
        self._statuses[config.name] = "registered"
        logger.info("PluginManager: registered %s", config.name)

    def unregister(self, name: str) -> None:
        self._plugins.pop(name, None)
        self._configs.pop(name, None)
        self._statuses.pop(name, None)
        logger.info("PluginManager: unregistered %s", name)

    def enable(self, name: str) -> bool:
        if name not in self._plugins:
            logger.warning("PluginManager: cannot enable unknown plugin %s", name)
            return False
        self._statuses[name] = "enabled"
        logger.info("PluginManager: enabled %s", name)
        return True

    def disable(self, name: str) -> bool:
        if name not in self._plugins:
            logger.warning("PluginManager: cannot disable unknown plugin %s", name)
            return False
        self._statuses[name] = "disabled"
        logger.info("PluginManager: disabled %s", name)
        return True

    def get_status(self, name: str) -> Optional[str]:
        return self._statuses.get(name)

    def list_by_category(self, category: str) -> list[dict]:
        results = []
        for name, config in self._configs.items():
            if getattr(config, "category", None) == category or (
                hasattr(config, "settings") and config.settings.get("category") == category
            ):
                results.append({
                    "name": name,
                    "config": config,
                    "status": self._statuses.get(name),
                })
        return results

    def list_plugins(self) -> list[str]:
        return list(self._plugins.keys())

    def get_module(self, name: str) -> Optional[PluginModule]:
        return self._plugins.get(name)