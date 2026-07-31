"""Real-world scenario: connect the NEXUS ERP (supermarket) to the financial
system, following the Volume 16 flow: analyze ERP -> create Connector ->
configure API -> map data -> test -> activate."""

from __future__ import annotations

from datetime import date

from integration.authentication.auth_engine import AuthEngine
from integration.authorization.permission_engine import PermissionEngine
from integration.connectors.connector_engine import ConnectorEngine
from integration.connectors.providers import register_all
from integration.events.event_engine import EventEngine
from integration.gateway.gateway_engine import GatewayEngine
from integration.integration_models import ConnectionConfig
from integration.marketplace.marketplace_engine import MarketplaceEngine
from integration.monitoring.monitoring_engine import MonitoringEngine
from integration.messaging.messaging_engine import MessagingEngine
from integration.synchronization.sync_engine import SynchronizationEngine
from integration.transformation.transform_engine import TransformationEngine
from integration.webhooks.webhook_engine import WebhookEngine


def _erp_engine() -> ConnectorEngine:
    engine = ConnectorEngine()
    register_all(engine.registry)
    return engine


def _erp_config() -> ConnectionConfig:
    return ConnectionConfig(
        name="nexus",
        connector_type="erp",
        config={"base_url": "https://nexus.local", "api_key": "secret"},
    )


class TestRealE2EFlow:
    """NEXUS ERP -> financial system integration (supermarket case)."""

    def test_analyze_erp(self) -> None:
        """Step 1: analyze the ERP and the systems it must reach."""
        engine = _erp_engine()
        config = _erp_config()
        assert engine.connect(config) is True
        # The financial flow: orders generated at the checkout must reach
        # the accounting/payments side.
        orders = engine.invoke(config, "list_orders")
        assert orders == {"orders": [], "count": 0}
        assert engine.invoke(config, "sync_financial") == {
            "synced": True, "source": "erp", "target": "financial"}

    def test_create_connector(self) -> None:
        """Step 2: register the connector between ERP and the financial system."""
        engine = _erp_engine()
        assert "erp" in engine.list_types()
        config = _erp_config()
        assert engine.connect(config) is True
        assert engine.check("conn-1", config).status == "ok"

    def test_configure_api(self) -> None:
        """Step 3: expose the financial API through the gateway with auth."""
        gateway = GatewayEngine()
        gateway.route("POST", "/api/financial/orders", lambda params: {"accepted": True})
        assert gateway.handle("POST", "/api/financial/orders") == {"accepted": True}

        auth = AuthEngine()
        api_key = auth.api_keys.issue("nexus-erp")
        assert auth.validate("api_key", api_key) is True

        perms = PermissionEngine()
        perms.define_role("erp-client", ["financial:orders:write"])
        perms.assign("nexus-erp", "erp-client")
        perms.enforce("nexus-erp", "financial:orders:write")

    def test_map_data(self) -> None:
        """Step 4: map ERP order fields to the financial order schema."""
        transformation = TransformationEngine()
        schema = transformation.schema_map()
        schema.field("numero_pedido", "str", rename_to="order_number")
        schema.field("total", "float", rename_to="amount")
        schema.field("data_emissao", "date", rename_to="issued_on")
        schema.field("pagamento", "str", rename_to="payment_method")

        erp_order = {
            "numero_pedido": "P-1042",
            "total": "289,90",
            "data_emissao": "2026-07-31",
            "pagamento": "pix",
        }
        financial = transformation.transform(schema, erp_order)
        assert financial == {
            "order_number": "P-1042",
            "amount": 289.9,
            "issued_on": date(2026, 7, 31),
            "payment_method": "pix",
        }

    def test_test_and_activate(self) -> None:
        """Step 5: test the integration, then activate it and monitor."""
        # Test: emit an order event through the pipeline.
        events = EventEngine()
        events.route("order.*", "financial")
        received: list[dict] = []
        events.on("financial", lambda e: received.append(e))
        events.emit("order.created", {"order_number": "P-1042", "amount": 289.9})
        events.drain()
        assert len(received) == 1

        # Activate: publish in the marketplace and mark the connector live.
        marketplace = MarketplaceEngine()
        marketplace.publish("nexus-erp", "NEXUS ERP", "erp",
                            description="ERP do supermercado", tags=["erp", "pix"])
        marketplace.install("nexus-erp", {"host": "erp.local"})
        assert marketplace.installer.is_installed("nexus-erp") is True

        # Monitor: health checks + metrics around the live integration.
        monitoring = MonitoringEngine()
        monitoring.probe("erp", lambda: True)
        monitoring.probe("financial", lambda: True)
        monitoring.metrics.increment("orders.synced", by=3)
        report = monitoring.report()
        assert report["status"] == "up"
        assert report["metrics"]["counters"]["orders.synced"] == 3

    def test_sync_financial_flow(self) -> None:
        """End-to-end: sync orders from ERP to the financial system."""
        engine = _erp_engine()
        config = _erp_config()
        assert engine.connect(config) is True
        created = engine.invoke(config, "create_order",
                                {"record": {"number": "N-100", "total": 289.9}})
        assert created["record"]["number"] == "N-100"
        orders = engine.invoke(config, "list_orders")
        assert orders["count"] == 1

        sync = SynchronizationEngine()
        result = sync.sync("nexus-erp", "financial", orders["orders"],
                           entity="orders")
        assert result["status"] == "completed"
        assert result["records_synced"] == orders["count"]

        # Delta sync: no changes -> nothing new to sync.
        again = sync.sync("nexus-erp", "financial", orders["orders"],
                          entity="orders")
        assert again["records_synced"] == 0

        # Notify downstream via webhook.
        webhooks = WebhookEngine(secret="supermarket")
        receipt = webhooks.notify(
            "https://financial.example.com/webhooks/orders",
            "orders.synced", {"job": result["job_id"]})
        assert receipt["delivered"] is True

        # Message the accounting topic.
        messaging = MessagingEngine()
        messaging.create_topic("accounting.orders", "pedidos para contabilidade")
        messaging.send("accounting.orders", {"job": result["job_id"]})
        assert messaging.stats()["messages"] == 1
