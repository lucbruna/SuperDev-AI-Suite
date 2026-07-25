import asyncio
import inspect
import logging
from typing import Any, Optional

from .plugin_context import PluginContext

logger = logging.getLogger(__name__)


class PluginRuntime:
    def __init__(self):
        self._loaded_modules: dict[str, Any] = {}
        self._sandbox = None

    def register_module(self, name: str, module: Any) -> None:
        self._loaded_modules[name] = module

    def unregister_module(self, name: str) -> None:
        self._loaded_modules.pop(name, None)

    async def _run_hooks(self, ctx: PluginContext, hook_type: str) -> None:
        hooks = ctx.config.settings.get("hooks", []) if ctx.config else []
        for hook in hooks:
            try:
                handler = hook.get(hook_type)
                if handler and callable(handler):
                    if asyncio.iscoroutinefunction(handler):
                        await handler(ctx)
                    else:
                        handler(ctx)
            except Exception as e:
                logger.error("Hook %s error for plugin %s: %s", hook_type, ctx.config.name if ctx.config else "unknown", e)

    async def execute(
        self, plugin_name: str, action: str, params: dict, ctx: PluginContext
    ) -> Any:
        module = self._loaded_modules.get(plugin_name)
        if not module:
            raise RuntimeError(f"Plugin {plugin_name} not loaded in runtime")

        self._current_ctx = ctx
        try:
            handler = getattr(module, action, None)
            if handler is None:
                raise AttributeError(f"Plugin {plugin_name} has no action '{action}'")

            sandbox = getattr(ctx, "_sandbox", None)
            if sandbox and hasattr(sandbox, "execute_safe"):
                result = await sandbox.execute_safe(plugin_name, handler, params)
            else:
                if asyncio.iscoroutinefunction(handler):
                    result = await handler(params, ctx)
                else:
                    result = handler(params, ctx)
            return result
        except Exception as e:
            logger.exception("Runtime execution error for %s.%s: %s", plugin_name, action, e)
            raise
        finally:
            self._current_ctx = None