from __future__ import annotations

import time
from typing import Any, Awaitable, Callable

from ..api_logger import APILogger

HandlerFunc = Callable[..., Awaitable[Any]]


class RouteMiddleware:
    """Middleware that executes at the route level during request processing."""

    def __init__(self, logger: APILogger | None = None) -> None:
        self._logger = logger or APILogger(__name__)

    async def timing(self, handler: HandlerFunc, **context: Any) -> Any:
        start = time.monotonic()
        try:
            return await handler(**context)
        finally:
            elapsed = time.monotonic() - start
            context.get("_route", "unknown")
            method = context.get("_method", "?")
            self._logger.debug(f"{method} {context.get('_route', '?')} took {elapsed:.3f}s")

    async def logging(self, handler: HandlerFunc, **context: Any) -> Any:
        route = context.get("_route", "?")
        method = context.get("_method", "?")
        self._logger.info(f"→ {method} {route}")
        try:
            result = await handler(**context)
            self._logger.info(f"← {method} {route} OK")
            return result
        except Exception as exc:
            self._logger.error(f"✗ {method} {route}: {exc}")
            raise

    async def validate_params(self, handler: HandlerFunc, **context: Any) -> Any:
        """Ensure required path params are present and non-empty."""
        for key, value in context.items():
            if key.startswith("_") and key != "_params":
                continue
            if key == "_params":
                for pkey, pvalue in value.items():
                    if pvalue is None or (isinstance(pvalue, str) and not pvalue.strip()):
                        raise ValueError(f"Required path parameter '{pkey}' is empty")
        return await handler(**context)

    @staticmethod
    def chain(handler: HandlerFunc, middlewares: list[Callable[..., Awaitable[Any]]]) -> HandlerFunc:
        """Compose a chain of middleware around a handler."""

        async def wrapped(**context: Any) -> Any:
            async def execute(index: int = 0) -> Any:
                if index < len(middlewares):
                    return await middlewares[index](execute, **context)
                return await handler(**context)

            return await execute()

        return wrapped
