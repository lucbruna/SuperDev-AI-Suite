from __future__ import annotations

import inspect
from typing import Any

from .api_events import APIEventBus, APIEventType
from .api_logger import APILogger
from .api_manager import APIManager


class APIShutdown:
    """Orchestrates the API Engine graceful shutdown sequence."""

    def __init__(self, manager: APIManager) -> None:
        self._manager = manager
        self._shutdown_hooks: list[tuple[str, Any]] = []

    def add_hook(self, name: str, hook: Any) -> None:
        self._shutdown_hooks.append((name, hook))

    async def run(self) -> None:
        logger: APILogger = self._manager.logger
        events: APIEventBus = self._manager.events

        logger.info("Shutting down API Engine")

        for name, hook in reversed(self._shutdown_hooks):
            try:
                result: Any = hook(self._manager) if callable(hook) else hook
                if inspect.isawaitable(result):
                    await result
                logger.info("Shutdown hook completed", hook=name)
            except Exception as e:
                logger.error("Shutdown hook failed", hook=name, error=str(e))

        await events.emit(APIEventType.SERVER_STOPPED, {})
        logger.info("API Engine shut down")

    def to_dict(self) -> dict[str, Any]:
        return {
            "hooks": [n for n, _ in self._shutdown_hooks],
            "hook_count": len(self._shutdown_hooks),
        }
