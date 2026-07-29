"""
Tests for the Financial AI Engine core components.
"""

import pytest
from datetime import datetime
from ..financial_engine import FinancialEngine, EngineConfig, EngineState, EngineMetrics
from ..treasury_manager import TreasuryManager, ManagerConfig
from ..finance_context import FinanceContext
from ..financial_events import FinancialEventBus, FinancialEvent, EventType
from ..financial_models import (
    TreasuryPosition, CashflowForecast, FinancialStatement,
    Transaction, TransactionType, TransactionStatus,
    AccountType, BudgetReport, AuditReport, RiskAssessment,
)
from ..financial_config import FinancialConfig
from ..financial_security import FinancialSecurityManager


class TestFinancialEngine:
    @pytest.mark.asyncio
    async def test_initialize(self):
        config = FinancialConfig()
        event_bus = FinancialEventBus()
        context = FinanceContext()
        engine_config = EngineConfig(config=config, event_bus=event_bus, context=context)
        engine = FinancialEngine(engine_config)
        await engine.initialize()
        assert engine.metrics.state == EngineState.RUNNING

    @pytest.mark.asyncio
    async def test_stop(self):
        config = FinancialConfig()
        event_bus = FinancialEventBus()
        context = FinanceContext()
        engine_config = EngineConfig(config=config, event_bus=event_bus, context=context)
        engine = FinancialEngine(engine_config)
        await engine.initialize()
        await engine.stop()
        assert engine.metrics.state == EngineState.STOPPED


class TestTreasuryManager:
    @pytest.mark.asyncio
    async def test_get_cash_position(self):
        config = FinancialConfig()
        event_bus = FinancialEventBus()
        context = FinanceContext()
        engine_config = EngineConfig(config=config, event_bus=event_bus, context=context)
        manager_config = ManagerConfig(engine_config=engine_config)
        manager = TreasuryManager(manager_config)
        await manager.initialize()
        position = await manager.get_cash_position()
        assert position is not None
        assert position.cash_balance > 0
        await manager.shutdown()

    @pytest.mark.asyncio
    async def test_get_cashflow_forecast(self):
        config = FinancialConfig()
        event_bus = FinancialEventBus()
        context = FinanceContext()
        engine_config = EngineConfig(config=config, event_bus=event_bus, context=context)
        manager_config = ManagerConfig(engine_config=engine_config)
        manager = TreasuryManager(manager_config)
        await manager.initialize()
        forecast = await manager.get_cashflow_forecast(30)
        assert forecast is not None
        assert forecast.horizon_days == 30
        await manager.shutdown()

    @pytest.mark.asyncio
    async def test_get_kpis(self):
        config = FinancialConfig()
        event_bus = FinancialEventBus()
        context = FinanceContext()
        engine_config = EngineConfig(config=config, event_bus=event_bus, context=context)
        manager_config = ManagerConfig(engine_config=engine_config)
        manager = TreasuryManager(manager_config)
        await manager.initialize()
        kpis = await manager.get_kpis()
        assert kpis is not None
        assert len(kpis) > 0
        await manager.shutdown()


class TestFinancialEventBus:
    @pytest.mark.asyncio
    async def test_publish_subscribe(self):
        bus = FinancialEventBus()
        received = []

        async def handler(event):
            received.append(event)

        bus.subscribe(EventType.CASH_POSITION_UPDATED, handler)
        event = FinancialEvent(event_type=EventType.CASH_POSITION_UPDATED, payload={"test": True})
        await bus.publish_nowait(event)
        assert len(received) == 1
        assert received[0].event_type == EventType.CASH_POSITION_UPDATED

    def test_event_counts(self):
        bus = FinancialEventBus()
        assert bus.get_event_count(EventType.CASH_LOW) == 0


class TestFinancialSecurity:
    def test_access_control(self):
        security = FinancialSecurityManager()
        security.set_user_role("cfi1", "cfi")
        assert security.check_access("cfi1", "financial", "read") is True
        assert security.check_access("cfi1", "financial", "audit") is True

    def test_encryption(self):
        security = FinancialSecurityManager()
        data = {"price": 100.50, "name": "Test"}
        encrypted = security.encrypt(data)
        assert encrypted["price"] != 100.50
        decrypted = security.decrypt(encrypted)
        assert float(decrypted["price"]) == 100.50

    def test_audit(self):
        security = FinancialSecurityManager()
        entry = security.audit({"type": "payment", "user_id": "user1", "resource": "PAY-001", "action": "approve"})
        assert entry["id"] is not None


class TestFinancialModels:
    def test_treasury_position(self):
        pos = TreasuryPosition(cash_balance=500000.0, bank_balance=450000.0)
        assert pos.total_liquidity == 0
        pos.total_liquidity = pos.cash_balance + pos.bank_balance + pos.short_term_investments
        assert pos.total_liquidity > 0

    def test_transaction_status(self):
        tx = Transaction(id="T-001", type=TransactionType.PAYMENT, description="Pagamento", amount=5000.0)
        assert tx.status == TransactionStatus.PENDING

    def test_financial_statement(self):
        fs = FinancialStatement(period="monthly", start_date=datetime.utcnow(), end_date=datetime.utcnow(),
                                total_revenue=1000000.0, total_expenses=700000.0, net_income=300000.0)
        assert fs.net_income == 300000.0


class TestIntegration:
    @pytest.mark.asyncio
    async def test_treasury_to_audit_flow(self):
        config = FinancialConfig()
        event_bus = FinancialEventBus()
        context = FinanceContext()
        engine_config = EngineConfig(config=config, event_bus=event_bus, context=context)
        manager_config = ManagerConfig(engine_config=engine_config)
        manager = TreasuryManager(manager_config)
        await manager.initialize()

        position = await manager.get_cash_position()
        assert position.cash_balance == 680000.0

        forecast = await manager.get_cashflow_forecast(7)
        assert forecast.horizon_days == 7

        investment = await manager.analyze_investment({"name": "Novo Projeto", "investment": 500000.0, "expected_return": 100000.0})
        assert investment is not None

        audit = await manager.run_audit()
        assert audit.status == "completed"

        health = await manager.get_financial_health_score()
        assert "score" in health

        await manager.shutdown()


if __name__ == "__main__":
    pytest.main(["-v", __file__])