from __future__ import annotations

import sys
from typing import Any

import pytest  # type: ignore[import-untyped]

sys.path.insert(0, "SuperDev")

from api.graphql import GraphQLServer, GraphQLSchema, ResolverRegistry  # noqa: E402
from api.graphql.subscriptions import SubscriptionManager  # noqa: E402
from api.graphql.middleware import GraphQLMiddleware  # noqa: E402


class TestGraphQLSchema:
    def test_schema_creation(self) -> None:
        schema = GraphQLSchema()
        assert schema is not None

    def test_type_registration(self) -> None:
        schema = GraphQLSchema()
        schema.add_type("User", {"id": "ID!", "name": "String!"})
        assert "User" in schema.get_types()


class TestResolverRegistry:
    def test_register_resolver(self) -> None:
        registry = ResolverRegistry()
        async def resolve_user() -> dict[str, Any]:
            return {"id": "1", "name": "Alice"}
        registry.register("Query", "user", resolve_user)
        assert registry.get_resolver("Query", "user") is resolve_user


class TestSubscriptionManager:
    def test_subscribe(self) -> None:
        mgr = SubscriptionManager()
        mgr.subscribe("sub1", "userUpdated")
        assert mgr.get_subscribers("userUpdated") == ["sub1"]

    def test_unsubscribe(self) -> None:
        mgr = SubscriptionManager()
        mgr.subscribe("sub1", "userUpdated")
        mgr.unsubscribe("sub1")
        assert mgr.get_subscribers("userUpdated") == []


class TestGraphQLMiddleware:
    def test_middleware_chain(self) -> None:
        mw = GraphQLMiddleware()
        called: list[str] = []
        mw.use(lambda next, ctx: (called.append("before"), next())[1])  # type: ignore[arg-type, return-value]
        assert len(mw.get_middlewares()) == 1


class TestGraphQLServer:
    def test_server_initialization(self) -> None:
        server = GraphQLServer()
        assert isinstance(server.schema, GraphQLSchema)
        assert isinstance(server.resolvers, ResolverRegistry)
