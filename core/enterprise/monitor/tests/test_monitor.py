import pytest

from core.enterprise.monitor.engine_adapters import (
    CustomerAdapter,
    DecisionCenterAdapter,
    FinancialAdapter,
    HRAdapter,
    KnowledgeAdapter,
    LegalAdapter,
    MultimodalAdapter,
    PhysicalAdapter,
    SupplyChainAdapter,
)
from core.enterprise.monitor.enterprise_monitor import EnterpriseMonitor


@pytest.fixture
async def monitor():
    m = EnterpriseMonitor()
    await m.initialize()
    yield m
    await m.shutdown()


@pytest.mark.asyncio
async def test_initialization():
    m = EnterpriseMonitor()
    assert len(m._adapters) == 9
    await m.initialize()
    assert m.is_healthy() is True
    await m.shutdown()


@pytest.mark.asyncio
async def test_get_enterprise_health(monitor):
    health = await monitor.get_enterprise_health()
    assert len(health) == 9
    for engine_name, info in health.items():
        assert "status" in info
        assert "healthy" in info
        assert info["healthy"] is True


@pytest.mark.asyncio
async def test_get_enterprise_kpis(monitor):
    kpis = await monitor.get_enterprise_kpis()
    assert len(kpis) == 9
    for engine_name, engine_kpis in kpis.items():
        assert isinstance(engine_kpis, dict)
        assert len(engine_kpis) >= 4


@pytest.mark.asyncio
async def test_get_enterprise_summary(monitor):
    summary = await monitor.get_enterprise_summary()
    assert summary["total_engines"] == 9
    assert summary["healthy_engines"] == 9
    assert summary["unhealthy_engines"] == 0
    assert summary["all_healthy"] is True
    assert summary["total_kpis"] >= 36
    assert len(summary["engine_names"]) == 9


@pytest.mark.asyncio
async def test_get_unified_dashboard(monitor):
    dashboard = await monitor.get_unified_dashboard()
    assert "health" in dashboard
    assert "kpis" in dashboard
    assert "summary" in dashboard
    assert len(dashboard["health"]) == 9
    assert len(dashboard["kpis"]) == 9
    assert dashboard["summary"]["all_healthy"] is True


@pytest.mark.asyncio
async def test_shutdown():
    m = EnterpriseMonitor()
    await m.initialize()
    assert m.is_healthy() is True
    await m.shutdown()


@pytest.mark.asyncio
async def test_is_healthy(monitor):
    assert monitor.is_healthy() is True


@pytest.mark.asyncio
async def test_get_engine_names(monitor):
    names = monitor.get_engine_names()
    expected = [
        "supply_chain",
        "financial",
        "hr",
        "legal",
        "customer",
        "decision_center",
        "physical",
        "multimodal",
        "knowledge",
    ]
    assert names == expected


@pytest.mark.asyncio
async def test_individual_adapter_supply_chain():
    adapter = SupplyChainAdapter()
    assert adapter.get_adapter_name() == "supply_chain"
    kpis = adapter.extract_kpis()
    assert "inventory_total" in kpis
    assert "inventory_value" in kpis
    assert "orders_pending" in kpis
    assert "supply_chain_health_score" in kpis
    health = adapter.get_health()
    assert health["engine"] == "supply_chain"
    assert health["healthy"] is True


@pytest.mark.asyncio
async def test_individual_adapter_financial():
    adapter = FinancialAdapter()
    assert adapter.get_adapter_name() == "financial"
    kpis = adapter.extract_kpis()
    assert "cash_balance" in kpis
    assert "total_liquidity" in kpis
    assert "transactions_today" in kpis
    assert "financial_health_score" in kpis


@pytest.mark.asyncio
async def test_individual_adapter_hr():
    adapter = HRAdapter()
    assert adapter.get_adapter_name() == "hr"
    kpis = adapter.extract_kpis()
    assert "total_employees" in kpis
    assert "open_positions" in kpis
    assert "engagement_score" in kpis
    assert "satisfaction_score" in kpis


@pytest.mark.asyncio
async def test_individual_adapter_legal():
    adapter = LegalAdapter()
    assert adapter.get_adapter_name() == "legal"
    kpis = adapter.extract_kpis()
    assert "active_contracts" in kpis
    assert "compliance_score" in kpis
    assert "risk_score" in kpis
    assert "violations_count" in kpis


@pytest.mark.asyncio
async def test_individual_adapter_customer():
    adapter = CustomerAdapter()
    assert adapter.get_adapter_name() == "customer"
    kpis = adapter.extract_kpis()
    assert "total_customers" in kpis
    assert "open_tickets" in kpis
    assert "cx_health_score" in kpis
    assert "sentiment_score" in kpis


@pytest.mark.asyncio
async def test_individual_adapter_decision_center():
    adapter = DecisionCenterAdapter()
    assert adapter.get_adapter_name() == "decision_center"
    kpis = adapter.extract_kpis()
    assert "active_kpis" in kpis
    assert "active_insights" in kpis
    assert "active_predictions" in kpis
    assert "recommendations_count" in kpis


@pytest.mark.asyncio
async def test_individual_adapter_physical():
    adapter = PhysicalAdapter()
    assert adapter.get_adapter_name() == "physical"
    kpis = adapter.extract_kpis()
    assert "active_robots" in kpis
    assert "total_devices" in kpis
    assert "factory_health" in kpis
    assert "active_alerts" in kpis


@pytest.mark.asyncio
async def test_individual_adapter_multimodal():
    adapter = MultimodalAdapter()
    assert adapter.get_adapter_name() == "multimodal"
    kpis = adapter.extract_kpis()
    assert "inputs_processed" in kpis
    assert "sessions_active" in kpis
    assert "modalities_active" in kpis
    assert "avg_processing_time" in kpis


@pytest.mark.asyncio
async def test_individual_adapter_knowledge():
    adapter = KnowledgeAdapter()
    assert adapter.get_adapter_name() == "knowledge"
    kpis = adapter.extract_kpis()
    assert "total_entries" in kpis
    assert "active_knowledge" in kpis
    assert "graph_nodes" in kpis
    assert "graph_edges" in kpis
