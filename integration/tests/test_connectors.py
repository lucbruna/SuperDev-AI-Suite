"""Tests for the connectors subsystem (connectors/) including providers."""

from __future__ import annotations

import pytest

from integration.connectors.connector_engine import ConnectorEngine
from integration.connectors.connector_health import ConnectorHealth
from integration.connectors.connector_manager import ConnectorManager
from integration.connectors.connector_registry import ConnectorRegistry
from integration.connectors.connector_template import (
    BaseConnector,
    GenericConnector,
    ProviderConnector,
)
from integration.connectors.connector_validator import ConnectorValidator
from integration.connectors.providers import list_providers, register_all
from integration.connectors.providers.business.erp import ERPConnector
from integration.connectors.providers.payments.pix import PixConnector
from integration.connectors.providers.payments.stripe import StripeConnector
from integration.integration_models import ConnectionConfig


class TestConnectorRegistry:
    def test_register_and_create(self) -> None:
        registry = ConnectorRegistry()
        registry.register("erp", ERPConnector)
        assert registry.has("erp") is True
        assert registry.get("erp") is ERPConnector
        connector = registry.create("erp")
        assert isinstance(connector, ERPConnector)
        assert registry.create("missing") is None

    def test_list(self) -> None:
        registry = ConnectorRegistry()
        registry.register("erp", ERPConnector)
        registry.register("pix", PixConnector)
        assert registry.list() == ["erp", "pix"]


class TestConnectorValidator:
    def test_validate(self) -> None:
        validator = ConnectorValidator()
        validator.register_schema(
            "erp",
            {"base_url": {"required": True, "type": "str"}, "api_key": {"required": True}},
        )
        valid = ConnectionConfig(name="erp", connector_type="erp",
                                 config={"base_url": "https://erp", "api_key": "k"})
        invalid = ConnectionConfig(name="erp", connector_type="erp", config={})
        assert validator.is_valid(valid) is True
        assert validator.is_valid(invalid) is False
        errors = validator.validate(invalid)
        assert any("base_url" in error for error in errors)
        # unknown type -> no schema -> valid
        assert validator.is_valid(
            ConnectionConfig(name="x", connector_type="unknown", config={})
        ) is True

    def test_type_checking(self) -> None:
        validator = ConnectorValidator()
        validator.register_schema("t", {"port": {"type": "int"}})
        assert validator.is_valid(
            ConnectionConfig(name="t", connector_type="t", config={"port": "8080"})
        ) is False
        assert validator.is_valid(
            ConnectionConfig(name="t", connector_type="t", config={"port": 8080})
        ) is True


class TestConnectorHealth:
    def test_check_ok_and_error(self) -> None:
        health = ConnectorHealth()
        report_ok = health.check("db", lambda: {"ok": True, "message": ""})
        assert report_ok.status == "ok"
        report_bad = health.check("api", lambda: {"ok": False, "message": "down"})
        assert report_bad.status == "error"
        assert report_bad.message == "down"

    def test_check_exception(self) -> None:
        health = ConnectorHealth()

        def boom() -> dict:
            raise RuntimeError("boom")

        report = health.check("svc", boom)
        assert report.status == "error"
        assert "boom" in report.message

    def test_connector_probe(self) -> None:
        health = ConnectorHealth()
        connector = GenericConnector("test")
        connector.connect(ConnectionConfig(name="t", connector_type="test"))
        report = health.check_connector("conn-1", connector)
        assert report.status == "ok"

    def test_snapshot(self) -> None:
        health = ConnectorHealth()
        health.check("a", lambda: {"ok": True})
        health.check("b", lambda: {"ok": False})
        snapshot = health.snapshot()
        assert snapshot["total"] == 2
        assert snapshot["healthy"] == 1
        assert snapshot["unhealthy"] == 1


class TestBaseConnector:
    def test_lifecycle(self) -> None:
        connector = GenericConnector("test")
        assert connector.is_connected() is False
        config = ConnectionConfig(name="t", connector_type="test")
        assert connector.connect(config) is True
        assert connector.is_connected() is True
        assert connector.status() == "connected"
        assert connector.test() is True
        connector.disconnect()
        assert connector.is_connected() is False

    def test_invoke_operations(self) -> None:
        connector = GenericConnector("test")
        assert connector.invoke("ping") == {"pong": True}
        with pytest.raises(KeyError):
            connector.invoke("missing")
        assert connector.operations() == ["ping"]

    def test_connect_invalid_config(self) -> None:
        connector = GenericConnector("test")

        class Failing(GenericConnector):
            def _do_connect(self, config: ConnectionConfig) -> bool:
                return False

        failing = Failing("failing")
        assert failing.connect(ConnectionConfig(name="f", connector_type="failing")) is False
        assert failing.status() == "disconnected"


class TestProviderConnector:
    def test_record_store(self) -> None:
        connector = ProviderConnector()
        record = connector._add({"name": "x"})
        assert record["id"] == "1"
        assert connector._all() == [{"id": "1", "name": "x"}]
        assert connector._find("1") == {"id": "1", "name": "x"}
        assert connector._update("1", {"name": "y"}) == {"id": "1", "name": "y"}
        assert connector._delete("1") is True
        assert connector._delete("1") is False


class TestBuiltinProviders:
    def test_provider_library(self) -> None:
        providers = list_providers()
        assert len(providers) == 16
        assert "erp" in providers
        assert "pix" in providers
        assert "postgresql" in providers
        assert "aws" in providers
        assert "whatsapp" in providers
        assert "ecommerce" in providers

    def test_register_all(self) -> None:
        registry = ConnectorRegistry()
        register_all(registry)
        assert registry.has("erp") is True
        assert registry.has("stripe") is True
        assert len(registry.list()) == 16

    def test_erp_connector_flow(self) -> None:
        registry = ConnectorRegistry()
        register_all(registry)
        engine = ConnectorEngine()
        for connector_type in registry.list():
            connector_class = registry.get(connector_type)
            if connector_class is not None:
                engine.register(connector_type, connector_class)
        config = ConnectionConfig(
            name="nexus",
            connector_type="erp",
            config={"base_url": "https://nexus.local", "api_key": "secret"},
        )
        assert engine.connect(config) is True
        result = engine.invoke(config, "list_orders")
        assert result == {"orders": [], "count": 0}
        created = engine.invoke(config, "create_order", {"record": {"number": "N-100"}})
        assert created["record"]["number"] == "N-100"
        orders = engine.invoke(config, "list_orders")
        assert orders["count"] == 1
        assert engine.invoke(config, "sync_financial") == {"synced": True, "source": "erp",
                                                           "target": "financial"}
        report = engine.check("conn-1", config)
        assert report.status == "ok"

    def test_erp_requires_config(self) -> None:
        engine = ConnectorEngine()
        register_all(engine.registry)
        config = ConnectionConfig(name="bad", connector_type="erp", config={})
        assert engine.connect(config) is False

    def test_stripe_flow(self) -> None:
        engine = ConnectorEngine()
        register_all(engine.registry)
        config = ConnectionConfig(name="stripe", connector_type="stripe",
                                  config={"secret_key": "sk_test_x"})
        assert engine.connect(config) is True
        intent = engine.invoke(config, "create_payment_intent", {"amount": 1000, "currency": "brl"})
        assert intent["status"] == "requires_confirmation"
        confirmed = engine.invoke(config, "confirm_payment_intent", {"id": intent["id"]})
        assert confirmed["status"] == "succeeded"

    def test_pix_flow(self) -> None:
        engine = ConnectorEngine()
        register_all(engine.registry)
        config = ConnectionConfig(name="pix", connector_type="pix",
                                  config={"client_id": "c", "client_secret": "s"})
        assert engine.connect(config) is True
        charge = engine.invoke(config, "create_charge", {"amount_cents": 5000, "key": "cpf"})
        assert charge["status"] == "pending"
        charges = engine.invoke(config, "list_charges")
        assert charges["count"] == 1

    def test_invoke_not_connected_raises(self) -> None:
        engine = ConnectorEngine()
        register_all(engine.registry)
        config = ConnectionConfig(name="x", connector_type="erp",
                                  config={"base_url": "u", "api_key": "k"})
        with pytest.raises(RuntimeError):
            engine.invoke(config, "list_orders")

    def test_invalid_operation_raises(self) -> None:
        engine = ConnectorEngine()
        register_all(engine.registry)
        config = ConnectionConfig(name="x", connector_type="erp",
                                  config={"base_url": "u", "api_key": "k"})
        engine.connect(config)
        with pytest.raises(KeyError):
            engine.invoke(config, "nope")

    def test_connector_manager_snapshot(self) -> None:
        engine = ConnectorEngine()
        register_all(engine.registry)
        config = ConnectionConfig(name="x", connector_type="crm",
                                  config={"base_url": "u", "token": "t"})
        engine.connect(config)
        stats = engine.stats()
        assert stats["connector_types"] == 16
        assert stats["instances"] >= 1
