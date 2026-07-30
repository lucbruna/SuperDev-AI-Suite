from __future__ import annotations

import sys
from typing import Any

import pytest  # type: ignore[import-untyped]

sys.path.insert(0, "SuperDev")

from api.gateway import APIGateway, GatewayRouter  # noqa: E402


class TestGatewayRouter:
    def test_route_registration(self) -> None:
        router = GatewayRouter()
        router.register("/api/v1", "http://localhost:8080")
        route = router.resolve("/api/v1/users")
        assert route is not None
        assert route.target == "http://localhost:8080"

    def test_route_not_found(self) -> None:
        router = GatewayRouter()
        route = router.resolve("/unknown")
        assert route is None

    def test_multiple_routes(self) -> None:
        router = GatewayRouter()
        router.register("/api/v1", "http://localhost:8080")
        router.register("/api/v2", "http://localhost:8081")
        r1 = router.resolve("/api/v1/test")
        r2 = router.resolve("/api/v2/test")
        assert r1 is not None and r1.target == "http://localhost:8080"
        assert r2 is not None and r2.target == "http://localhost:8081"


class TestAPIGateway:
    def test_gateway_initialization(self) -> None:
        gateway = APIGateway()
        assert isinstance(gateway.router, GatewayRouter)

    def test_add_route(self) -> None:
        gateway = APIGateway()
        gateway.add_route("/api", "http://localhost:8080")
        resolved = gateway.resolve("/api/hello")
        assert resolved is not None
