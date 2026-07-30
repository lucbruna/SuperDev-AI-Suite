from __future__ import annotations

import time
from typing import Any, Callable

from ..api_logger import APILogger
from ..api_metrics import APIMetrics


class InterceptorChain:
    """Chain of gRPC interceptors for request/response processing."""

    def __init__(self) -> None:
        self._interceptors: list[dict[str, Any]] = []

    def register(self, name: str, interceptor_fn: Callable) -> None:
        self._interceptors.append({"name": name, "fn": interceptor_fn})

    async def intercept(self, method_handler: Callable, request: Any, context: Any) -> Any:
        async def run(index: int = 0) -> Any:
            if index < len(self._interceptors):
                mw = self._interceptors[index]
                return await mw["fn"](method_handler, request, context, lambda: run(index + 1))
            result = method_handler(request, context)
            if hasattr(result, "__await__"):
                return await result
            return result
        return await run()

    def to_dict(self) -> dict[str, Any]:
        return {"interceptors": [m["name"] for m in self._interceptors], "count": len(self._interceptors)}


async def logging_interceptor(
    method_handler: Callable,
    request: Any,
    context: Any,
    next_fn: Callable,
    logger: APILogger | None = None,
) -> Any:
    log = logger or APILogger("grpc.interceptor")
    log.info("gRPC call", method=getattr(method_handler, "__name__", "unknown"))
    result = await next_fn()
    log.info("gRPC call completed", method=getattr(method_handler, "__name__", "unknown"))
    return result


async def timing_interceptor(
    method_handler: Callable,
    request: Any,
    context: Any,
    next_fn: Callable,
    metrics: APIMetrics | None = None,
) -> Any:
    start = time.time()
    result = await next_fn()
    elapsed = (time.time() - start) * 1000
    if metrics:
        metrics.timing("grpc.call", elapsed, {"method": getattr(method_handler, "__name__", "unknown")})
    return result


async def auth_interceptor(
    method_handler: Callable,
    request: Any,
    context: Any,
    next_fn: Callable,
    authenticator: Any | None = None,
) -> Any:
    if authenticator and hasattr(authenticator, "authenticate"):
        metadata = getattr(context, "metadata", {})
        auth_result = await authenticator.authenticate(metadata)
        if not auth_result.get("authenticated"):
            raise PermissionError("gRPC authentication failed")
    return await next_fn()


async def error_interceptor(
    method_handler: Callable,
    request: Any,
    context: Any,
    next_fn: Callable,
) -> Any:
    try:
        return await next_fn()
    except Exception as e:
        return {"error": {"message": str(e), "code": "INTERNAL"}}
