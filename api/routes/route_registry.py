from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Awaitable, Callable

from ..api_logger import APILogger

HandlerFunc = Callable[..., Awaitable[Any]]
MiddlewareFunc = Callable[..., Awaitable[Any]]


class HTTPMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    TRACE = "TRACE"
    CONNECT = "CONNECT"


@dataclass
class RouteEntry:
    path: str
    methods: set[HTTPMethod]
    handler: HandlerFunc
    middlewares: list[MiddlewareFunc] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    pattern: re.Pattern = field(init=False)
    param_names: list[str] = field(init=False)

    def __post_init__(self) -> None:
        pattern_str = ""
        self.param_names = []
        raw_parts = self.path.split("/")
        parts = [p for p in raw_parts if p != ""]
        for part in parts:
            if part.startswith("{") and part.endswith("}"):
                name = part[1:-1]
                self.param_names.append(name)
                pattern_str += "/([^/]+)"
            elif part.startswith("{") and part.endswith("?}"):
                name = part[1:-2]
                self.param_names.append(name)
                pattern_str += "(?:/([^/]+))?"
            elif part == "*":
                pattern_str += "(?:/.*)?"
            else:
                pattern_str += "/" + re.escape(part)
        self.pattern = re.compile(f"^{pattern_str}$") if pattern_str else re.compile("^$")

    def match(self, request_path: str) -> dict[str, str] | None:
        match = self.pattern.match(request_path)
        if not match:
            return None
        return dict(zip(self.param_names, match.groups()))


class RouteRegistry:
    """Central registry mapping URL paths to handlers."""

    def __init__(self, logger: APILogger | None = None) -> None:
        self._routes: list[RouteEntry] = []
        self._named_routes: dict[str, RouteEntry] = {}
        self._logger = logger or APILogger(__name__)

    def register(
        self,
        path: str,
        handler: HandlerFunc,
        methods: list[HTTPMethod] | None = None,
        *,
        name: str | None = None,
        middlewares: list[MiddlewareFunc] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        if methods is None:
            methods = [HTTPMethod.GET]
        entry = RouteEntry(
            path=path,
            methods=set(methods),
            handler=handler,
            middlewares=middlewares or [],
            metadata=metadata or {},
        )
        self._routes.append(entry)
        if name:
            self._named_routes[name] = entry
        self._logger.debug(f"Registered route: {' '.join(m.value for m in methods)} {path}")

    def resolve(self, method: str, path: str) -> tuple[HandlerFunc, list[MiddlewareFunc], dict[str, str], dict[str, Any]] | None:
        method_enum = HTTPMethod(method.upper())
        for entry in self._routes:
            if method_enum not in entry.methods:
                continue
            params = entry.match(path)
            if params is not None:
                return entry.handler, entry.middlewares, params, entry.metadata
        return None

    def get_routes(self) -> list[RouteEntry]:
        return list(self._routes)

    def url_for(self, name: str, **params: str) -> str | None:
        entry = self._named_routes.get(name)
        if not entry:
            return None
        path = entry.path
        for key, value in params.items():
            path = path.replace(f"{{{key}}}", value)
        return path

    def clear(self) -> None:
        self._routes.clear()
        self._named_routes.clear()

    def __len__(self) -> int:
        return len(self._routes)
