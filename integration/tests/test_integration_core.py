"""Smoke tests for the Integration & API Engine core: config, models, events,
metrics, registry, security, context, runtime, manager, and engine facade.
"""

from __future__ import annotations

import pytest

from integration import (
    IntegrationConfig,
    IntegrationEngine,
    IntegrationFactory,
    IntegrationManager,
    IntegrationRegistry,
    IntegrationRuntime,
)
from integration.integration_context import IntegrationContext, IntegrationResult
from integration.integration_events import IntegrationEventType, IntegrationEvents
from integration.integration_metrics import IntegrationMetrics
from integration.integration_models import (
    APIEndpoint,
    ConnectionConfig,
    ConnectionRecord,
    ConnectorStatus,
    EventMessage,
    HealthReport,
    IntegrationDefinition,
    MessageRecord,
    MessageStatus,
    MonitorAlert,
    SyncRecord,
    SyncStatus,
    WebhookRecord,
)
from integration.integration_security import IntegrationSecurity


class TestIntegrationConfig:
    def test_defaults(self) -> None:
        config = IntegrationConfig()
        assert config.workspace_id == "default"
        assert config.gateway_port == 8080
        assert config.default_rate_limit == 100
        assert config.enable_auth is True

    def test_merge(self) -> None:
        config = IntegrationConfig()
        config.merge({"gateway_port": 9090, "custom": "x"})
        assert config.gateway_port == 9090
        assert config.extra["custom"] == "x"


class TestIntegrationModels:
    def test_connection_config_to_dict(self) -> None:
        config = ConnectionConfig(name="ERP", connector_type="erp", config={"host": "h"})
        data = config.to_dict()
        assert data["name"] == "ERP"
        assert data["connector_type"] == "erp"
        assert data["config"] == {"host": "h"}

    def test_connection_record_to_dict(self) -> None:
        record = ConnectionRecord(
            connection_id="conn-1",
            config=ConnectionConfig(name="x", connector_type="y"),
            status=ConnectorStatus.CONNECTED,
        )
        data = record.to_dict()
        assert data["connection_id"] == "conn-1"
        assert data["status"] == "connected"

    def test_api_endpoint(self) -> None:
        endpoint = APIEndpoint(method="GET", path="/orders", operation="list_orders")
        data = endpoint.to_dict()
        assert data["method"] == "GET"
        assert data["path"] == "/orders"
        assert data["version"] == "v1"

    def test_webhook_and_event(self) -> None:
        webhook = WebhookRecord(webhook_id="wh-1", url="https://x/cb", events=["order.created"])
        assert webhook.to_dict()["enabled"] is True
        message = EventMessage(event_type="order.created", payload={"id": 1})
        assert message.to_dict()["source"] == "integration"

    def test_message_and_sync_status(self) -> None:
        message = MessageRecord(queue="q1", payload={"x": 1})
        assert message.status == MessageStatus.PENDING
        assert message.to_dict()["priority"] == 0
        sync = SyncRecord(sync_id="s-1", connection_id="conn-1")
        assert sync.status == SyncStatus.PENDING

    def test_health_and_alert(self) -> None:
        health = HealthReport(component="erp")
        assert health.status == "ok"
        alert = MonitorAlert(alert_id="a-1", severity="critical", message="down")
        assert alert.to_dict()["resolved"] is False

    def test_integration_definition(self) -> None:
        definition = IntegrationDefinition(
            integration_id="int-1", name="NEXUS ERP", category="business", provider="nexus"
        )
        assert definition.to_dict()["provider"] == "nexus"


class TestIntegrationEvents:
    def test_publish_subscribe(self) -> None:
        events = IntegrationEvents()
        received: list[tuple[str, dict]] = []

        def listener(event_type: str, payload: dict) -> None:
            received.append((event_type, payload))

        events.on(IntegrationEventType.CONNECTION_CREATED, listener)
        events.emit(IntegrationEventType.CONNECTION_CREATED, {"connection_id": "c1"})
        assert received == [(IntegrationEventType.CONNECTION_CREATED, {"connection_id": "c1"})]

    def test_off_and_once(self) -> None:
        events = IntegrationEvents()
        calls = {"n": 0}

        def listener(event_type: str, payload: dict) -> None:
            calls["n"] += 1

        events.once(IntegrationEventType.ERROR, listener)
        events.emit(IntegrationEventType.ERROR)
        events.emit(IntegrationEventType.ERROR)
        assert calls["n"] == 1
        assert events.listener_count(IntegrationEventType.ERROR) == 0

    def test_listener_isolation(self) -> None:
        events = IntegrationEvents()

        def bad_listener(event_type: str, payload: dict) -> None:
            raise RuntimeError("boom")

        def good_listener(event_type: str, payload: dict) -> None:
            pass

        events.on(IntegrationEventType.EVENT_PUBLISHED, bad_listener)
        events.on(IntegrationEventType.EVENT_PUBLISHED, good_listener)
        events.emit(IntegrationEventType.EVENT_PUBLISHED)  # must not raise


class TestIntegrationMetrics:
    def test_increment_and_snapshot(self) -> None:
        metrics = IntegrationMetrics()
        metrics.increment("connections.created")
        metrics.increment("connections.created", 2)
        assert metrics.get("connections.created") == 3
        snapshot = metrics.snapshot()
        assert snapshot["counters"]["connections.created"] == 3

    def test_timing(self) -> None:
        metrics = IntegrationMetrics()
        with metrics.time("invoke"):
            pass
        assert metrics.average_timing("invoke") >= 0.0


class TestIntegrationRegistry:
    def test_register_and_get(self) -> None:
        registry = IntegrationRegistry()
        registry.register_connector("erp", object())
        assert registry.get_connector("erp") is not None
        registry.register_auth_provider("oauth", object())
        assert registry.get_auth_provider("oauth") is not None
        registry.register_transformer("mapper", object())
        assert registry.get_transformer("mapper") is not None
        snapshot = registry.snapshot()
        assert snapshot["connectors"] == 1
        assert snapshot["auth_providers"] == 1
        assert snapshot["transformers"] == 1

    def test_factories(self) -> None:
        registry = IntegrationRegistry()

        def factory(config: IntegrationConfig) -> str:
            return "built"

        registry.register_factory("connector:erp", factory)
        assert registry.get_factory("connector:erp") is factory
        assert registry.get_factory("missing") is None


class TestIntegrationSecurity:
    def test_sanitize_and_redact(self) -> None:
        security = IntegrationSecurity()
        assert security.sanitize("<script>") == "&lt;script&gt;"
        assert security.redact("super-secret-value", "api_key") == "***"
        assert security.redact_config({"api_key": "abc", "host": "h"})["api_key"] == "***"
        assert security.redact_config({"api_key": "abc", "host": "h"})["host"] == "h"

    def test_permissions(self) -> None:
        security = IntegrationSecurity()
        security.grant("alice", "connections.connect")
        assert security.check_permission("alice", "connections.connect") is True
        assert security.check_permission("alice", "connections.delete") is False
        security.grant("bob", "*")
        assert security.check_permission("bob", "anything") is True

    def test_enforce(self) -> None:
        security = IntegrationSecurity()
        with pytest.raises(PermissionError):
            security.enforce("bob", "connections.connect")

    def test_api_keys(self) -> None:
        security = IntegrationSecurity()
        key = security.issue_api_key("alice")
        assert key.startswith("sk-")
        assert security.validate_api_key(key) == "alice"
        assert security.revoke_api_key(key) is True
        assert security.validate_api_key(key) is None


class TestIntegrationFactory:
    def test_build_manager(self) -> None:
        factory = IntegrationFactory()
        manager = factory.build_manager()
        assert manager is not None
        assert manager.config.workspace_id == "default"

    def test_build_with_registry(self) -> None:
        registry = IntegrationRegistry()
        factory = IntegrationFactory(config=IntegrationConfig(workspace_id="w9"), registry=registry)
        manager = factory.build_manager()
        assert manager.config.workspace_id == "w9"


class TestIntegrationRuntime:
    def test_start_stop(self) -> None:
        runtime = IntegrationRuntime()
        assert runtime.is_running is False
        runtime.start()
        assert runtime.is_running is True
        assert runtime.manager is not None
        status = runtime.status()
        assert status["started"] is True
        runtime.stop()
        assert runtime.is_running is False

    def test_start_idempotent(self) -> None:
        runtime = IntegrationRuntime()
        runtime.start()
        manager = runtime.manager
        runtime.start()
        assert runtime.manager is manager


class TestIntegrationManager:
    def test_create_and_list_connections(self) -> None:
        manager = IntegrationManager()
        connection_id = manager.create_connection(
            ConnectionConfig(name="ERP", connector_type="erp")
        )
        assert connection_id.startswith("conn-")
        assert len(manager.list_connections()) == 1
        record = manager.get_connection(connection_id)
        assert record is not None
        assert record.config.name == "ERP"

    def test_remove_connection(self) -> None:
        manager = IntegrationManager()
        connection_id = manager.create_connection(
            ConnectionConfig(name="x", connector_type="y")
        )
        assert manager.remove_connection(connection_id) is True
        assert manager.remove_connection(connection_id) is False

    def test_register_endpoint_and_route(self) -> None:
        manager = IntegrationManager()
        key = manager.register_endpoint(
            APIEndpoint(method="GET", path="/orders", operation="list")
        )
        assert key == "GET /orders"
        assert manager.get_endpoint("GET", "/orders") is not None
        assert len(manager.list_endpoints()) == 1

    def test_status(self) -> None:
        manager = IntegrationManager()
        manager.create_connection(ConnectionConfig(name="x", connector_type="y"))
        status = manager.status()
        assert status["connections"] == 1
        assert "metrics" in status
        assert "registry" in status

    def test_invoke_unconnected_raises(self) -> None:
        manager = IntegrationManager()
        connection_id = manager.create_connection(
            ConnectionConfig(name="x", connector_type="y")
        )
        with pytest.raises(RuntimeError):
            manager.invoke(connection_id, "op")


class TestIntegrationEngine:
    def test_initialize_and_shutdown(self) -> None:
        engine = IntegrationEngine().initialize()
        assert engine.status()["started"] is True
        engine.shutdown()
        assert engine.status()["started"] is False

    def test_create_connection_flow(self) -> None:
        engine = IntegrationEngine().initialize()
        result = engine.create_connection(ConnectionConfig(name="ERP", connector_type="erp"))
        assert result.success is True
        assert result.operation == "create_connection"
        connection_id = result.data["connection_id"]
        connections = engine.list_connections()
        assert connections.success is True
        assert len(connections.data) == 1
        engine.shutdown()

    def test_connect_uninitialized_fails(self) -> None:
        engine = IntegrationEngine()
        result = engine.connect("conn-1")
        assert result.success is False
        assert "not initialized" in result.error

    def test_install_integration(self) -> None:
        engine = IntegrationEngine().initialize()
        result = engine.install_integration(
            IntegrationDefinition(integration_id="int-1", name="NEXUS", category="business")
        )
        assert result.success is True
        assert engine.registry.get_provider("int-1") is not None
        engine.shutdown()

    def test_result_envelope(self) -> None:
        ok_result = IntegrationResult.ok("op", {"x": 1})
        assert ok_result.success is True and ok_result.operation == "op"
        fail_result = IntegrationResult.fail("op", "nope")
        assert fail_result.success is False and fail_result.error == "nope"

    def test_context_with_attributes(self) -> None:
        context = IntegrationContext(workspace_id="w1", user="alice", connection_id="c1")
        context.with_attributes(trace_id="t-1")
        assert context.get("trace_id") == "t-1"
        assert context.to_dict()["connection_id"] == "c1"
