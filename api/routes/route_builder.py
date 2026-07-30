from __future__ import annotations

from typing import Any, Awaitable, Callable

from ..api_logger import APILogger
from .route_registry import HTTPMethod, HandlerFunc, MiddlewareFunc, RouteRegistry


class RouteBuilder:
    """Fluent API for constructing and registering routes."""

    def __init__(self, registry: RouteRegistry, logger: APILogger | None = None) -> None:
        self._registry = registry
        self._logger = logger or APILogger(__name__)
        self._path: str = ""
        self._methods: list[HTTPMethod] = []
        self._handler: HandlerFunc | None = None
        self._middlewares: list[MiddlewareFunc] = []
        self._metadata: dict[str, Any] = {}
        self._name: str | None = None

    def path(self, path: str) -> RouteBuilder:
        self._path = path
        return self

    def methods(self, *methods: HTTPMethod) -> RouteBuilder:
        self._methods = list(methods)
        return self

    def get(self) -> RouteBuilder:
        self._methods.append(HTTPMethod.GET)
        return self

    def post(self) -> RouteBuilder:
        self._methods.append(HTTPMethod.POST)
        return self

    def put(self) -> RouteBuilder:
        self._methods.append(HTTPMethod.PUT)
        return self

    def patch(self) -> RouteBuilder:
        self._methods.append(HTTPMethod.PATCH)
        return self

    def delete(self) -> RouteBuilder:
        self._methods.append(HTTPMethod.DELETE)
        return self

    def handler(self, handler: HandlerFunc) -> RouteBuilder:
        self._handler = handler
        return self

    def middleware(self, *mw: MiddlewareFunc) -> RouteBuilder:
        self._middlewares.extend(mw)
        return self

    def metadata(self, **kwargs: Any) -> RouteBuilder:
        self._metadata.update(kwargs)
        return self

    def name(self, name: str) -> RouteBuilder:
        self._name = name
        return self

    def register(self) -> None:
        if not self._path or not self._handler or not self._methods:
            raise ValueError("path, handler, and at least one method are required")
        self._registry.register(
            path=self._path,
            handler=self._handler,
            methods=self._methods,
            name=self._name,
            middlewares=self._middlewares,
            metadata=self._metadata,
        )
        self._logger.info(f"Built route: {' '.join(m.value for m in self._methods)} {self._path}")

    def group(self, prefix: str) -> RouteGroup:
        return RouteGroup(self._registry, prefix, self._logger)


class RouteGroup:
    """Route group that shares a common prefix."""

    def __init__(self, registry: RouteRegistry, prefix: str, logger: APILogger) -> None:
        self._registry = registry
        self._prefix = prefix.rstrip("/")
        self._logger = logger
        self._middlewares: list[MiddlewareFunc] = []

    def middleware(self, *mw: MiddlewareFunc) -> RouteGroup:
        self._middlewares.extend(mw)
        return self

    def route(self, path: str) -> RouteBuilder:
        full_path = f"{self._prefix}/{path.lstrip('/')}"
        builder = RouteBuilder(self._registry, self._logger)
        builder.path(full_path)
        for mw in self._middlewares:
            builder.middleware(mw)
        return builder
