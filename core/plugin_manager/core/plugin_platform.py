import asyncio
import logging
import os
from pathlib import Path
from typing import Optional

from .plugin_configuration import PluginConfig
from .plugin_manager import PluginManager
from .plugin_runtime import PluginRuntime
from .plugin_context import PluginContext
from .plugin_health import check_plugin_health

logger = logging.getLogger(__name__)


class PluginPlatform:
    _instance: Optional["PluginPlatform"] = None
    _lock: asyncio.Lock = asyncio.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._initialized = False
            self._manager = PluginManager()
            self._runtime = PluginRuntime()
            self._plugin_dir: Path = Path.cwd() / "plugins"
            self._configs: dict[str, PluginConfig] = {}
            self._contexts: dict[str, PluginContext] = {}

    async def initialize(self, plugin_dir: Optional[str | Path] = None) -> None:
        async with self._lock:
            if self._initialized:
                logger.warning("PluginPlatform already initialized")
                return
            if plugin_dir:
                self._plugin_dir = Path(plugin_dir)
            self._plugin_dir.mkdir(parents=True, exist_ok=True)
            self._initialized = True
            logger.info("PluginPlatform initialized with plugin_dir=%s", self._plugin_dir)

    async def shutdown(self) -> None:
        async with self._lock:
            if not self._initialized:
                return
            shutdown_tasks = []
            for name in list(self._manager.list_plugins()):
                ctx = self._contexts.get(name)
                if ctx:
                    shutdown_tasks.append(self._runtime._run_hooks(ctx, "shutdown"))
            if shutdown_tasks:
                await asyncio.gather(*shutdown_tasks, return_exceptions=True)
            self._manager = PluginManager()
            self._configs.clear()
            self._contexts.clear()
            self._initialized = False
            logger.info("PluginPlatform shut down")

    async def install_plugin(self, source: str | Path) -> PluginConfig:
        from ..installer.install import PluginInstaller
        installer = PluginInstaller(self._plugin_dir)
        manifest = await installer.install(source)
        config = PluginConfig(
            id=manifest.name,
            name=manifest.name,
            version=manifest.version,
            entrypoint=manifest.entrypoint,
            permissions=manifest.permissions,
            dependencies=manifest.dependencies,
            settings={},
        )
        self._configs[config.name] = config
        from ..loader.plugin_loader import PluginLoader
        loader = PluginLoader(self._plugin_dir)
        module = await loader.load(manifest)
        self._manager.register(module, config)
        logger.info("Plugin installed: %s v%s", config.name, config.version)
        return config

    async def uninstall_plugin(self, name: str) -> bool:
        config = self._configs.get(name)
        if not config:
            logger.warning("Plugin not found: %s", name)
            return False
        self._manager.unregister(name)
        self._configs.pop(name, None)
        self._contexts.pop(name, None)
        from ..installer.uninstall import PluginUninstaller
        uninstaller = PluginUninstaller(self._plugin_dir)
        result = await uninstaller.uninstall(name)
        logger.info("Plugin uninstalled: %s", name)
        return result

    def get_plugin(self, name: str) -> Optional[PluginConfig]:
        return self._configs.get(name)

    def list_plugins(self) -> list[PluginConfig]:
        return list(self._configs.values())

    async def execute(self, plugin_name: str, action: str, params: dict = None) -> any:
        config = self._configs.get(plugin_name)
        if not config:
            raise ValueError(f"Plugin {plugin_name} not found")
        ctx = self._contexts.get(plugin_name)
        if not ctx:
            ctx = PluginContext(api={}, storage={}, events=[], config=config)
            self._contexts[plugin_name] = ctx
        return await self._runtime.execute(plugin_name, action, params or {}, ctx)