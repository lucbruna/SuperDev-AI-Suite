from __future__ import annotations

import inspect
from typing import Any

from .api_events import APIEventBus, APIEventType
from .api_logger import APILogger
from .api_manager import APIManager


class APIStartup:
    """Orchestrates the API Engine startup sequence."""

    def __init__(self, manager: APIManager) -> None:
        self._manager = manager
        self._startup_hooks: list[tuple[str, Any]] = []

    def add_hook(self, name: str, hook: Any) -> None:
        self._startup_hooks.append((name, hook))

    async def run(self) -> None:
        logger: APILogger = self._manager.logger
        events: APIEventBus = self._manager.events

        logger.info("Starting API Engine", version=self._manager.version.version)

        for name, hook in self._startup_hooks:
            try:
                result: Any = hook(self._manager) if callable(hook) else hook
                if inspect.isawaitable(result):
                    await result
                logger.info("Startup hook completed", hook=name)
            except Exception as e:
                logger.error("Startup hook failed", hook=name, error=str(e))
                raise

        await events.emit(APIEventType.SERVER_STARTED, {"version": self._manager.version.version})
        logger.info("API Engine started successfully")

    def to_dict(self) -> dict[str, Any]:
        return {
            "hooks": [n for n, _ in self._startup_hooks],
            "hook_count": len(self._startup_hooks),
        }
