from __future__ import annotations

import json
from typing import Any

from ..api_interfaces import IAPIRouter
from ..api_models import APIRequest, APIResponse
from ..api_registry import APIRegistry
from ..api_runtime import APIRuntime
from .request import RequestParser
from .router import RESTRouter


class RESTfulServer:
    """Core REST server that processes HTTP requests through the API pipeline."""

    def __init__(self, registry: APIRegistry, runtime: APIRuntime) -> None:
        self._registry = registry
        self._runtime = runtime
        self._router = RESTRouter()
        self._parser = RequestParser()

    @property
    def router(self) -> RESTRouter:
        return self._router

    def get(self, path: str, handler: Any, **metadata: Any) -> None:
        self._router.get(path, handler, **metadata)

    def post(self, path: str, handler: Any, **metadata: Any) -> None:
        self._router.post(path, handler, **metadata)

    def put(self, path: str, handler: Any, **metadata: Any) -> None:
        self._router.put(path, handler, **metadata)

    def patch(self, path: str, handler: Any, **metadata: Any) -> None:
        self._router.patch(path, handler, **metadata)

    def delete(self, path: str, handler: Any, **metadata: Any) -> None:
        self._router.delete(path, handler, **metadata)

    async def handle_scope(self, scope: dict[str, Any], body_bytes: bytes) -> APIResponse:
        request: APIRequest = self._parser.parse(scope, body_bytes)
        return await self._runtime.process_request(request)

    def register_routes(self, app: Any) -> None:
        self._router.register_routes(app)

    def to_dict(self) -> dict[str, Any]:
        return {
            "subsystem": "rest",
            "routes": len(self._router.get_routes()),
            "registered": self._router.to_dict().get("registered", False),
        }
