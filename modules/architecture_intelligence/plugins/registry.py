"""Plugin registry for third-party intelligence extensions.

Plugins are callables keyed by name; the registry invokes them during reports
and agent runs. Registration is idempotent and failures never block core work.
"""
from __future__ import annotations

import threading
from typing import Any, Callable

Plugin = Callable[..., Any]


class PluginRegistry:
    def __init__(self) -> None:
        self._plugins: dict[str, Plugin] = {}
        self._lock = threading.Lock()

    def register(self, name: str, plugin: Plugin) -> None:
        with self._lock:
            self._plugins[name] = plugin

    def unregister(self, name: str) -> None:
        with self._lock:
            self._plugins.pop(name, None)

    def names(self) -> list[str]:
        with self._lock:
            return sorted(self._plugins)

    def run(self, name: str, **kwargs: Any) -> dict[str, Any]:
        with self._lock:
            plugin = self._plugins.get(name)
        if plugin is None:
            return {"plugin": name, "ok": False, "error": "not registered"}
        try:
            result = plugin(**kwargs)
            return {"plugin": name, "ok": True, "result": result}
        except Exception as exc:  # pragma: no cover - defensive
            return {"plugin": name, "ok": False, "error": str(exc)}

    def run_all(self, **kwargs: Any) -> list[dict[str, Any]]:
        return [self.run(name, **kwargs) for name in self.names()]


_registry: PluginRegistry | None = None
_registry_lock = threading.Lock()


def get_plugin_registry() -> PluginRegistry:
    global _registry
    if _registry is None:
        with _registry_lock:
            if _registry is None:
                _registry = PluginRegistry()
    return _registry


def register_plugin(name: str, plugin: Plugin) -> None:
    get_plugin_registry().register(name, plugin)
