"""AIOS REST Gateway — declarative route registry.

Registers (method, path) -> handler with ``{param}`` placeholders and
dispatches requests deterministically. The actual HTTP transport is
out of scope here; this models the contract a FastAPI adapter satisfies.
"""

from __future__ import annotations

import inspect
import re
import time
from typing import Any, Awaitable, Callable

RouteHandler = Callable[[dict[str, Any], dict[str, Any]], Awaitable[dict[str, Any]] | dict[str, Any]]

_PARAM_RE = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")


class RESTGateway:
    """Path-based route registry with parameter extraction."""

    def __init__(self) -> None:
        self._routes: list[tuple[str, str, re.Pattern[str], tuple[str, ...], RouteHandler]] = []
        self._calls: list[dict[str, Any]] = []

    def register(self, method: str, path: str, handler: RouteHandler) -> "RESTGateway":
        pattern = re.compile("^" + _PARAM_RE.sub(r"(?P<\1>[^/]+)", path) + "$")
        params = tuple(_PARAM_RE.findall(path))
        self._routes.append((method.upper(), path, pattern, params, handler))
        return self

    def routes(self) -> list[str]:
        return [path for _, path, _, _, _ in self._routes]

    async def handle(
        self, method: str, path: str, query: dict[str, Any] | None = None, body: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        method = method.upper()
        started = time.perf_counter()
        for route_method, route_path, pattern, params, handler in self._routes:
            if route_method != method:
                continue
            match = pattern.match(path)
            if match is None:
                continue
            path_params = {name: match.group(name) for name in params}
            request = {"path": path, "method": method, "query": query or {}, "body": body or {}}
            try:
                outcome = handler(request, path_params)
                if inspect.isawaitable(outcome):
                    outcome = await outcome
                result: dict[str, Any] = {"ok": True, "result": outcome}
            except Exception as exc:  # noqa: BLE001
                result = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
            self._calls.append(
                {
                    "method": method,
                    "route": route_path,
                    "path": path,
                    "ok": result.get("ok", False),
                    "elapsed_ms": round((time.perf_counter() - started) * 1000, 3),
                }
            )
            return {"method": method, "path": path, **result}
        return {"ok": False, "error": f"route not found: {method} {path}", "method": method, "path": path}

    def snapshot(self) -> dict[str, Any]:
        return {"routes": self.routes(), "calls": len(self._calls)}
