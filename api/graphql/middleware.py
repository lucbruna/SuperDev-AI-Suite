from __future__ import annotations

import time
from typing import Any, Callable

from ..api_logger import APILogger
from ..api_metrics import APIMetrics


class GraphQLMiddleware:
    """Simple middleware chain for GraphQL resolvers."""

    def __init__(self) -> None:
        self._middleware: list[Callable] = []

    def use(self, fn: Callable) -> None:
        self._middleware.append(fn)

    def get_middlewares(self) -> list[Callable]:
        return list(self._middleware)

    def __len__(self) -> int:
        return len(self._middleware)


class MiddlewareChain:
    """Chain of GraphQL middleware functions."""

    def __init__(self) -> None:
        self._middleware: list[dict[str, Any]] = []

    def use(self, name: str, fn: Callable) -> None:
        self._middleware.append({"name": name, "fn": fn})

    async def execute(self, resolve_fn: Callable, parent: Any, args: dict[str, Any], context: Any) -> Any:
        async def run(index: int = 0) -> Any:
            if index < len(self._middleware):
                mw = self._middleware[index]
                return await mw["fn"](resolve_fn, parent, args, context, lambda: run(index + 1))
            result = resolve_fn(parent, args, context)
            if hasattr(result, "__await__"):
                return await result
            return result
        return await run()

    def to_dict(self) -> dict[str, Any]:
        return {"middleware": [m["name"] for m in self._middleware], "count": len(self._middleware)}


async def apply_middleware(
    resolve_fn: Callable,
    parent: Any,
    args: dict[str, Any],
    context: Any,
    chain: MiddlewareChain | None = None,
) -> Any:
    """Apply middleware chain and execute resolver."""
    if chain is None:
        chain = MiddlewareChain()
    return await chain.execute(resolve_fn, parent, args, context)


async def logging_middleware(
    resolve_fn: Callable,
    parent: Any,
    args: dict[str, Any],
    context: Any,
    next_fn: Callable,
    logger: APILogger | None = None,
) -> Any:
    log = logger or APILogger("graphql.middleware")
    log.info("Resolving", field=getattr(resolve_fn, "__name__", "unknown"))
    result = await next_fn()
    log.info("Resolved", field=getattr(resolve_fn, "__name__", "unknown"))
    return result


async def timing_middleware(
    resolve_fn: Callable,
    parent: Any,
    args: dict[str, Any],
    context: Any,
    next_fn: Callable,
    metrics: APIMetrics | None = None,
) -> Any:
    start = time.time()
    result = await next_fn()
    elapsed = (time.time() - start) * 1000
    if metrics:
        metrics.timing("graphql.resolver", elapsed, {"field": getattr(resolve_fn, "__name__", "unknown")})
    return result
