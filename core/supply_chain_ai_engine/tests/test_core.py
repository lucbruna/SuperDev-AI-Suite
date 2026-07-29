"""
Tests for the Supply Chain AI Engine core components.
"""

import pytest
from datetime import datetime
from ..supply_chain_engine import SupplyChainEngine, EngineConfig, EngineState
from ..supply_manager import SupplyChainManager, ManagerConfig
from ..supply_context import SupplyChainContext
from ..supply_events import SupplyChainEventBus, SupplyChainEvent, EventType
from ..supply_models import (
    InventoryItem, InventorySnapshot, Product, Supplier,
    ProcurementOrder, OrderStatus, StockStatus,
)
from ..supply_config import SupplyChainConfig
from ..supply_security import SupplySecurityManager


class TestSupplyChainEngine:
    @pytest.mark.asyncio
    async def test_initialize(self):
        config = SupplyChainConfig()
        event_bus = SupplyChainEventBus()
        context = SupplyChainContext()
        engine_config = EngineConfig(config=config, event_bus=event_bus, context=context)
        engine = SupplyChainEngine(engine_config)
        await engine.initialize()
        assert engine.metrics.state == EngineState.RUNNING

    @pytest.mark.asyncio
    async def test_stop(self):
        config = SupplyChainConfig()
        event_bus = SupplyChainEventBus()
        context = SupplyChainContext()
        engine_config = EngineConfig(config=config, event_bus=event_bus, context=context)
        engine = SupplyChainEngine(engine_config)
        await engine.initialize()
        await engine.stop()
        assert engine.metrics.state == EngineState.STOPPED


class TestSupplyChainManager:
    @pytest.mark.asyncio
    async def test_get_inventory_snapshot(self):
        config = SupplyChainConfig()
        event_bus = SupplyChainEventBus()
        context = SupplyChainContext()
        engine_config = EngineConfig(config=config, event_bus=event_bus, context=context)
        manager_config = ManagerConfig(engine_config=engine_config)
        manager = SupplyChainManager(manager_config)
        await manager.initialize()
        snapshot = await manager.get_inventory_snapshot()
        assert snapshot is not None
        assert snapshot.total_items > 0
        await manager.shutdown()

    @pytest.mark.asyncio
    async def test_get_demand_forecast(self):
        config = SupplyChainConfig()
        event_bus = SupplyChainEventBus()
        context = SupplyChainContext()
        engine_config = EngineConfig(config=config, event_bus=event_bus, context=context)
        manager_config = ManagerConfig(engine_config=engine_config)
        manager = SupplyChainManager(manager_config)
        await manager.initialize()
        forecast = await manager.get_demand_forecast(30)
        assert forecast is not None
        assert forecast.horizon_days == 30
        await manager.shutdown()

    @pytest.mark.asyncio
    async def test_get_kpis(self):
        config = SupplyChainConfig()
        event_bus = SupplyChainEventBus()
        context = SupplyChainContext()
        engine_config = EngineConfig(config=config, event_bus=event_bus, context=context)
        manager_config = ManagerConfig(engine_config=engine_config)
        manager = SupplyChainManager(manager_config)
        await manager.initialize()
        kpis = await manager.get_kpis()
        assert kpis is not None
        assert len(kpis) > 0
        await manager.shutdown()


class TestSupplyChainEventBus:
    @pytest.mark.asyncio
    async def test_publish_subscribe(self):
        bus = SupplyChainEventBus()
        received = []

        async def handler(event):
            received.append(event)

        bus.subscribe(EventType.INVENTORY_LOW, handler)
        event = SupplyChainEvent(event_type=EventType.INVENTORY_LOW, payload={"test": True})
        await bus.publish_nowait(event)
        assert len(received) == 1
        assert received[0].event_type == EventType.INVENTORY_LOW

    def test_event_counts(self):
        bus = SupplyChainEventBus()
        assert bus.get_event_count(EventType.INVENTORY_LOW) == 0


class TestSupplyChainSecurity:
    def test_access_control(self):
        security = SupplySecurityManager()
        security.set_user_role("user1", "admin")
        assert security.check_access("user1", "inventory", "read") is True
        assert security.check_access("user1", "inventory", "configure") is True

    def test_encryption(self):
        security = SupplySecurityManager()
        data = {"price": 100.50, "name": "Produto Teste"}
        encrypted = security.encrypt(data)
        assert encrypted["price"] != 100.50
        decrypted = security.decrypt(encrypted)
        assert float(decrypted["price"]) == 100.50

    def test_audit(self):
        security = SupplySecurityManager()
        entry = security.audit({"type": "purchase_order", "user_id": "user1", "resource": "PO-001", "action": "create"})
        assert entry.id is not None
        assert entry.status == "success"


class TestSupplyChainModels:
    def test_inventory_item(self):
        item = InventoryItem(product_id="test", sku="TEST-001", product_name="Teste",
                             current_stock=100, reorder_point=50, optimal_level=200)
        assert item.available == 100
        assert item.is_low is False
        item.reserved_stock = 60
        assert item.available == 40
        assert item.is_low is True

    def test_inventory_snapshot(self):
        items = {"P1": InventoryItem(product_id="P1", sku="SKU1", product_name="P1", current_stock=10)}
        snapshot = InventorySnapshot(items=items)
        assert snapshot.get_product_quantity("P1") == 10

    def test_procurement_order_status(self):
        order = ProcurementOrder(id="PO-TEST", supplier_id="SUP-001", items={"SKU1": 10})
        assert order.status == OrderStatus.DRAFT
        assert order.is_emergency is False


if __name__ == "__main__":
    pytest.main(["-v", __file__])