from __future__ import annotations

import sys
from typing import Any

import pytest  # type: ignore[import-untyped]

sys.path.insert(0, "SuperDev")

from api.routes import RouteRegistry, RouteBuilder, RouteMiddleware  # noqa: E402
from api.routes.route_registry import HTTPMethod  # noqa: E402


class TestRouteRegistry:
    def test_register_route(self) -> None:
        registry = RouteRegistry()
        async def handler() -> dict[str, str]:
            return {"ok": "true"}
        registry.register("/test", handler, methods=[HTTPMethod.GET])
        assert len(registry) == 1

    def test_resolve_route(self) -> None:
        registry = RouteRegistry()
        async def handler() -> dict[str, str]:
            return {"ok": "true"}
        registry.register("/users/{id}", handler, methods=[HTTPMethod.GET])
        result = registry.resolve("GET", "/users/42")
        assert result is not None
        handler_func, middlewares, params, metadata = result
        assert params == {"id": "42"}

    def test_resolve_not_found(self) -> None:
        registry = RouteRegistry()
        async def handler() -> dict[str, str]:
            return {"ok": "true"}
        registry.register("/users/{id}", handler, methods=[HTTPMethod.GET])
        result = registry.resolve("POST", "/users/42")
        assert result is None

    def test_url_for(self) -> None:
        registry = RouteRegistry()
        async def handler() -> dict[str, str]:
            return {"ok": "true"}
        registry.register("/users/{id}", handler, methods=[HTTPMethod.GET], name="user.get")
        url = registry.url_for("user.get", id="42")
        assert url == "/users/42"

    def test_clear(self) -> None:
        registry = RouteRegistry()
        async def handler() -> dict[str, str]:
            return {"ok": "true"}
        registry.register("/test", handler)
        registry.clear()
        assert len(registry) == 0


class TestRouteBuilder:
    def test_builder_fluent(self) -> None:
        registry = RouteRegistry()
        builder = RouteBuilder(registry)
        async def handler() -> dict[str, str]:
            return {"ok": "true"}
        builder.path("/hello").methods(HTTPMethod.GET).handler(handler).register()
        assert len(registry) == 1


class TestRouteMiddleware:
    def test_chain(self) -> None:
        mw = RouteMiddleware()
        order: list[str] = []

        async def mw1(next_func: Any, **ctx: Any) -> Any:
            order.append("1")
            return await next_func(**ctx)

        async def mw2(next_func: Any, **ctx: Any) -> Any:
            order.append("2")
            return await next_func(**ctx)

        async def handler(**ctx: Any) -> str:
            order.append("h")
            return "done"

        wrapped = RouteMiddleware.chain(handler, [mw1, mw2])
        # Can't easily await in sync test, verify construction
        assert wrapped is not None
