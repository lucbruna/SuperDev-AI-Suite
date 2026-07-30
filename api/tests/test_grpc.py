from __future__ import annotations

import sys
from typing import Any

import pytest  # type: ignore[import-untyped]

sys.path.insert(0, "SuperDev")

from api.grpc import GrpcServer, ServiceRegistry, MethodDefinition  # noqa: E402
from api.grpc.interceptor_chain import InterceptorChain  # noqa: E402


class TestServiceRegistry:
    def test_register_service(self) -> None:
        registry = ServiceRegistry()
        registry.register_service("UserService")
        assert "UserService" in registry.list_services()

    def test_register_method(self) -> None:
        registry = ServiceRegistry()
        method = MethodDefinition(
            name="GetUser",
            input_type="GetUserRequest",
            output_type="GetUserResponse",
        )
        registry.register_method("UserService", method)
        methods = registry.get_methods("UserService")
        assert len(methods) == 1
        assert methods[0].name == "GetUser"

    def test_register_method_unregistered_service(self) -> None:
        registry = ServiceRegistry()
        method = MethodDefinition(
            name="GetUser",
            input_type="GetUserRequest",
            output_type="GetUserResponse",
        )
        registry.register_method("UserService", method)
        # Should auto-register service
        assert "UserService" in registry.list_services()


class TestInterceptorChain:
    def test_interceptor_chain(self) -> None:
        chain = InterceptorChain()
        order: list[str] = []

        async def interceptor1(next_func: Any, ctx: Any) -> Any:
            order.append("i1")
            return await next_func(ctx)

        async def interceptor2(next_func: Any, ctx: Any) -> Any:
            order.append("i2")
            return await next_func(ctx)

        chain.add(interceptor1)
        chain.add(interceptor2)
        assert len(chain.interceptors) == 2


class TestGrpcServer:
    def test_server_initialization(self) -> None:
        server = GrpcServer("0.0.0.0", 50051)
        assert server.host == "0.0.0.0"
        assert server.port == 50051
        assert isinstance(server.registry, ServiceRegistry)
