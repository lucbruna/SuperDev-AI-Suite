"""Tests for the API management subsystem (api/)."""

from __future__ import annotations

import pytest

from integration.api.api_builder import ApiBuilder
from integration.api.api_engine import ApiEngine
from integration.api.api_generator import ApiGenerator
from integration.api.api_registry import ApiRegistry
from integration.api.documentation import ApiDocumentation
from integration.api.endpoint_manager import EndpointManager
from integration.api.schema_manager import SchemaManager
from integration.api.versioning import ApiVersioning
from integration.integration_models import APIEndpoint, IntegrationDefinition


class TestApiRegistry:
    def test_register_and_get(self) -> None:
        registry = ApiRegistry()
        endpoint = APIEndpoint(method="GET", path="/orders", operation="list")
        key = registry.register(endpoint)
        assert key == "GET /orders"
        assert registry.get("GET", "/orders") is endpoint
        assert registry.get("POST", "/orders") is None
        assert registry.count() == 1

    def test_remove_and_clear(self) -> None:
        registry = ApiRegistry()
        registry.register(APIEndpoint(method="GET", path="/a", operation="op"))
        assert registry.remove("GET", "/a") is True
        assert registry.remove("GET", "/a") is False
        registry.register(APIEndpoint(method="POST", path="/b", operation="op"))
        registry.clear()
        assert registry.count() == 0


class TestEndpointManager:
    def test_crud(self) -> None:
        manager = EndpointManager()
        endpoint = manager.create("get", "/orders", "list_orders")
        assert endpoint.method == "GET"
        assert manager.get("GET", "/orders") is endpoint
        endpoint.description = "list all"
        assert manager.update(endpoint) is True
        assert manager.delete("GET", "/orders") is True
        assert manager.delete("GET", "/orders") is False

    def test_list_filter_by_version(self) -> None:
        manager = EndpointManager()
        manager.create("GET", "/v1/orders", "op", version="v1")
        manager.create("GET", "/v2/orders", "op", version="v2")
        assert len(manager.list()) == 2
        assert len(manager.list(version="v1")) == 1

    def test_bind_route(self) -> None:
        manager = EndpointManager()
        manager.bind("GET", "/orders", "conn-1", "list")
        route = manager.route_for("GET", "/orders")
        assert route == {"connection_id": "conn-1", "operation": "list"}
        assert manager.route_for("GET", "/missing") is None


class TestSchemaManager:
    def test_validate_object(self) -> None:
        schemas = SchemaManager()
        schemas.register(
            "order",
            {
                "type": "object",
                "required": ["id"],
                "properties": {"id": {"type": "int"}, "status": {"type": "str"}},
            },
        )
        assert schemas.validate("order", {"id": 1, "status": "open"}) is True
        assert schemas.validate("order", {"status": "open"}) is False
        assert schemas.validate("order", {"id": "x"}) is False

    def test_validate_list_and_enum(self) -> None:
        schemas = SchemaManager()
        schemas.register("ids", {"type": "list", "items": {"type": "int"}})
        assert schemas.validate("ids", [1, 2, 3]) is True
        assert schemas.validate("ids", [1, "x"]) is False
        schemas.register("status", {"type": "str", "enum": ["open", "closed"]})
        assert schemas.validate("status", "open") is True
        assert schemas.validate("status", "other") is False

    def test_unknown_schema_raises(self) -> None:
        schemas = SchemaManager()
        with pytest.raises(KeyError):
            schemas.validate("missing", {})

    def test_scalar_types(self) -> None:
        schemas = SchemaManager()
        schemas.register("n", {"type": "float"})
        assert schemas.validate("n", 1.5) is True
        assert schemas.validate("n", True) is False


class TestApiBuilder:
    def test_build_from_spec(self) -> None:
        builder = ApiBuilder()
        endpoint = builder.build(
            {"method": "post", "path": "/webhook", "operation": "notify"}
        )
        assert endpoint.method == "POST"
        assert endpoint.path == "/webhook"
        assert endpoint.version == "v1"
        assert endpoint.auth_required is True

    def test_build_missing_fields_raises(self) -> None:
        builder = ApiBuilder()
        with pytest.raises(ValueError):
            builder.build({"method": "GET"})

    def test_build_many(self) -> None:
        builder = ApiBuilder()
        endpoints = builder.build_many(
            [
                {"method": "GET", "path": "/a", "operation": "op_a"},
                {"method": "POST", "path": "/b", "operation": "op_b"},
            ]
        )
        assert len(endpoints) == 2

    def test_from_connector(self) -> None:
        builder = ApiBuilder()
        endpoints = builder.from_connector("erp", ["list_orders", "get_product"], "/erp")
        assert len(endpoints) == 2
        assert all(e.path.startswith("/erp/") for e in endpoints)
        assert endpoints[0].operation == "list_orders"


class TestApiGenerator:
    def test_generate_from_definition(self) -> None:
        generator = ApiGenerator()
        definition = IntegrationDefinition(
            integration_id="nexus", name="NEXUS ERP", provider="nexus", version="2.0.0"
        )
        endpoints = generator.generate(definition, ["sync", "health"], "/v1")
        assert len(endpoints) == 2
        assert all(e.version == "2.0.0" for e in endpoints)
        assert endpoints[0].metadata["integration_id"] == "nexus"

    def test_openapi(self) -> None:
        generator = ApiGenerator()
        endpoints = [APIEndpoint(method="GET", path="/orders", operation="list")]
        doc = generator.openapi(endpoints)
        assert doc["openapi"] == "3.0.0"
        assert "/orders" in doc["paths"]
        assert doc["paths"]["/orders"]["get"]["operationId"] == "list"


class TestApiDocumentation:
    def test_describe(self) -> None:
        docs = ApiDocumentation()
        endpoint = APIEndpoint(method="GET", path="/orders", operation="list",
                               description="list orders")
        data = docs.describe(endpoint)
        assert data["method"] == "GET"
        assert data["description"] == "list orders"

    def test_markdown(self) -> None:
        docs = ApiDocumentation()
        md = docs.markdown([APIEndpoint(method="GET", path="/orders", operation="list")])
        assert "## GET /orders" in md
        assert "Operation: `list`" in md


class TestApiVersioning:
    def test_resolve(self) -> None:
        versioning = ApiVersioning()
        v1 = APIEndpoint(method="GET", path="/orders", operation="list", version="v1")
        v2 = APIEndpoint(method="GET", path="/orders", operation="list", version="v2")
        endpoints = [v1, v2]
        assert versioning.resolve(endpoints, "v2") is v2
        assert versioning.resolve(endpoints, "v3") is None

    def test_latest_and_versions(self) -> None:
        versioning = ApiVersioning()
        endpoints = [
            APIEndpoint(method="GET", path="/a", operation="op", version="v1"),
            APIEndpoint(method="GET", path="/b", operation="op", version="v2"),
        ]
        assert versioning.latest(endpoints) is not None
        latest = versioning.latest(endpoints)
        assert latest is not None and latest.version == "v2"
        assert versioning.versions(endpoints) == ["v1", "v2"]
        assert versioning.latest([]) is None

    def test_path_for(self) -> None:
        versioning = ApiVersioning()
        endpoint = APIEndpoint(method="GET", path="/v1/orders", operation="list", version="v1")
        assert versioning.path_for(endpoint, "v2") == "/v2/orders"
        endpoint2 = APIEndpoint(method="GET", path="/orders", operation="list", version="v1")
        assert versioning.path_for(endpoint2, "v2") == "/v2/orders"


class TestApiEngine:
    def test_register_and_list(self) -> None:
        engine = ApiEngine()
        endpoint = APIEndpoint(method="GET", path="/orders", operation="list")
        engine.register(endpoint)
        assert engine.get("GET", "/orders") is endpoint
        assert len(engine.list()) == 1
        assert engine.stats()["endpoints"] == 1

    def test_register_spec_and_remove(self) -> None:
        engine = ApiEngine()
        endpoint = engine.register_spec(
            {"method": "POST", "path": "/webhook", "operation": "notify"}
        )
        assert endpoint.method == "POST"
        assert engine.remove("POST", "/webhook") is True
        assert engine.get("POST", "/webhook") is None

    def test_schemas(self) -> None:
        engine = ApiEngine()
        engine.register_schema("order", {"type": "object", "required": ["id"]})
        assert engine.validate("order", {"id": 1}) is True
        assert engine.validate("order", {}) is False

    def test_openapi_and_markdown(self) -> None:
        engine = ApiEngine()
        engine.register(APIEndpoint(method="GET", path="/orders", operation="list"))
        doc = engine.openapi()
        assert doc["paths"] != {}
        md = engine.markdown_docs()
        assert "## GET /orders" in md
