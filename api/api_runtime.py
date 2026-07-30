from __future__ import annotations

import time
from typing import Any

from .api_context import APIContext
from .api_events import APIEventBus, APIEventType
from .api_logger import APILogger
from .api_metrics import APIMetrics
from .api_models import APIRequest, APIResponse
from .api_registry import APIRegistry


class APIRuntime:
    """Runtime engine for processing API requests through the pipeline."""

    def __init__(self, registry: APIRegistry, logger: APILogger, metrics: APIMetrics, events: APIEventBus) -> None:
        self._registry = registry
        self._logger = logger
        self._metrics = metrics
        self._events = events
        self._middleware: list[Any] = []

    def add_middleware(self, mw: Any) -> None:
        self._middleware.append(mw)

    async def process_request(self, request: APIRequest) -> APIResponse:
        start = time.time()
        context = APIContext(request)
        self._metrics.increment("requests")

        try:
            await self._events.emit(APIEventType.REQUEST_STARTED, {"path": request.path, "method": request.method})

            for mw in self._middleware:
                result = await mw.before_request(request) if hasattr(mw, "before_request") else None
                if result and isinstance(result, APIResponse):
                    return result

            route = self._registry.get_route(request.method, request.path)
            if not route:
                return APIResponse(status_code=404, body={"error": "Not Found", "path": request.path})

            handler = route["handler"]
            response = await handler(request, context) if hasattr(handler, "__call__") else handler

            for mw in reversed(self._middleware):
                if hasattr(mw, "after_request"):
                    response = await mw.after_request(response)

            elapsed_ms = (time.time() - start) * 1000
            response.elapsed_ms = round(elapsed_ms, 2)
            response.request_id = request.request_id

            self._metrics.timing("request.duration", elapsed_ms)
            await self._events.emit(APIEventType.REQUEST_COMPLETED, {"path": request.path, "status": response.status_code})

            return response

        except Exception as e:
            elapsed_ms = (time.time() - start) * 1000
            self._logger.error(f"Request failed: {e}", path=request.path, method=request.method)
            self._metrics.increment("errors")
            await self._events.emit(APIEventType.REQUEST_FAILED, {"path": request.path, "error": str(e)})

            return APIResponse(status_code=500, body={"error": "Internal Server Error"}, request_id=request.request_id, elapsed_ms=round(elapsed_ms, 2))

    async def process_stream(self, request: APIRequest) -> Any:
        route = self._registry.get_route(request.method, request.path)
        if not route:
            return
        handler = route["handler"]
        async for chunk in handler(request, None):
            yield chunk
