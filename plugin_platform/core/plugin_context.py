from __future__ import annotations

import logging
from typing import Any, Callable, Optional

from .plugin_configuration import PluginConfig

logger = logging.getLogger(__name__)


class PluginContext:
    def __init__(
        self,
        api: dict[str, Any],
        storage: dict[str, Any],
        events: list[dict],
        config: PluginConfig,
        sandbox: Any = None,
    ):
        self._api = api
        self._storage = storage
        self._events = events
        self._config = config
        self._sandbox = sandbox
        self._hooks: dict[str, list[Callable]] = {}

    @property
    def api(self) -> dict[str, Any]:
        return dict(self._api)

    @property
    def storage(self) -> dict[str, Any]:
        return self._storage

    @property
    def config(self) -> PluginConfig:
        return self._config

    def get_api_endpoint(self, name: str) -> Optional[Any]:
        return self._api.get(name)

    def store_value(self, key: str, value: Any) -> None:
        self._storage[key] = value

    def get_value(self, key: str) -> Optional[Any]:
        return self._storage.get(key)

    def emit_event(self, event_name: str, payload: dict = None) -> None:
        event = {"name": event_name, "payload": payload or {}, "plugin": self._config.name}
        self._events.append(event)
        logger.debug("Event emitted: %s from %s", event_name, self._config.name)

    def register_hook(self, hook_name: str, callback: Callable) -> None:
        if hook_name not in self._hooks:
            self._hooks[hook_name] = []
        self._hooks[hook_name].append(callback)

    def run_hooks(self, hook_name: str, *args, **kwargs) -> list[Any]:
        results = []
        for callback in self._hooks.get(hook_name, []):
            try:
                results.append(callback(*args, **kwargs))
            except Exception as e:
                logger.error("Hook %s callback error: %s", hook_name, e)
        return results