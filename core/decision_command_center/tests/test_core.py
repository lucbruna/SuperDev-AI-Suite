"""
Tests for the Decision Command Center core components.
"""

import pytest
from datetime import datetime
from ..decision_engine import DecisionEngine, EngineConfig, EngineState, EngineMetrics
from ..command_center import CommandCenter, ManagerConfig
from ..decision_config import DecisionConfig
from ..decision_security import DecisionSecurityManager
from ..decision_models import (
    KPI, Insight, InsightType, AlertSeverity, BusinessArea, Prediction,
    Recommendation, RecommendationPriority, Scenario, ScenarioType,
    SimulationResult, Dashboard, DashboardType, ExecutiveSummary,
    Alert, RevenueForecast, BoardReport,
)
from ..dashboard_manager import DashboardManager
from ..insight_manager import InsightManager
from ..strategy_engine import StrategyEngine
from ..simulation_engine import SimulationEngine as SimulationEngineCore


class TestDecisionEngine:
    @pytest.mark.asyncio
    async def test_initialize(self):
        config = DecisionConfig()
        security = DecisionSecurityManager(config)
        engine_config = EngineConfig(config=config, security=security)
        engine = DecisionEngine(engine_config)
        await engine.initialize()
        assert engine.metrics.state == EngineState.RUNNING

    @pytest.mark.asyncio
    async def test_stop(self):
        config = DecisionConfig()
        security = DecisionSecurityManager(config)
        engine_config = EngineConfig(config=config, security=security)
        engine = DecisionEngine(engine_config)
        await engine.initialize()
        await engine.stop()
        assert engine.metrics.state == EngineState.STOPPED


class TestCommandCenter:
    @pytest.mark.asyncio
    async def test_get_kpis(self):
        config = DecisionConfig()
        security = DecisionSecurityManager(config)
        engine_config = EngineConfig(config=config, security=security)
        manager_config = ManagerConfig(engine_config=engine_config)
        cc = CommandCenter(manager_config)
        await cc.initialize()
        kpis = await cc.get_kpis()
        assert kpis is not None
        assert len(kpis) > 0
        await cc.shutdown()

    @pytest.mark.asyncio
    async def test_get_insights(self):
        config = DecisionConfig()
        security = DecisionSecurityManager(config)
        engine_config = EngineConfig(config=config, security=security)
        manager_config = ManagerConfig(engine_config=engine_config)
        cc = CommandCenter(manager_config)
        await cc.initialize()
        insights = await cc.get_insights()
        assert len(insights) > 0
        await cc.shutdown()

    @pytest.mark.asyncio
    async def test_get_predictions(self):
        config = DecisionConfig()
        security = DecisionSecurityManager(config)
        engine_config = EngineConfig(config=config, security=security)
        manager_config = ManagerConfig(engine_config=engine_config)
        cc = CommandCenter(manager_config)
        await cc.initialize()
        predictions = await cc.get_predictions()
        assert len(predictions) > 0
        await cc.shutdown()

    @pytest.mark.asyncio
    async def test_get_recommendations(self):
        config = DecisionConfig()
        security = DecisionSecurityManager(config)
        engine_config = EngineConfig(config=config, security=security)
        manager_config = ManagerConfig(engine_config=engine_config)
        cc = CommandCenter(manager_config)
        await cc.initialize()
        recs = await cc.get_recommendations()
        assert len(recs) > 0
        await cc.shutdown()

    @pytest.mark.asyncio
    async def test_get_business_health(self):
        config = DecisionConfig()
        security = DecisionSecurityManager(config)
        engine_config = EngineConfig(config=config, security=security)
        manager_config = ManagerConfig(engine_config=engine_config)
        cc = CommandCenter(manager_config)
        await cc.initialize()
        health = await cc.get_business_health()
        assert "health_score" in health
        assert "status" in health
        await cc.shutdown()

    @pytest.mark.asyncio
    async def test_ceo_assistant(self):
        config = DecisionConfig()
        security = DecisionSecurityManager(config)
        engine_config = EngineConfig(config=config, security=security)
        manager_config = ManagerConfig(engine_config=engine_config)
        cc = CommandCenter(manager_config)
        await cc.initialize()
        answer = await cc.ask_ceo_assistant("Qual o maior problema da empresa?")
        assert "answer" in answer
        await cc.shutdown()


class TestDecisionSecurity:
    def test_access_control(self):
        security = DecisionSecurityManager()
        security.set_user_role("ceo1", "ceo")
        assert security.check_access("ceo1", "strategy", "read") is True
        assert security.check_access("ceo1", "strategy", "approve") is True

    def test_encryption(self):
        security = DecisionSecurityManager()
        data = {"strategy": "expand_to_market_x", "public_info": "visible"}
        encrypted = security.encrypt_strategic_data(data)
        assert encrypted["strategy"] != "expand_to_market_x"
        assert encrypted["public_info"] == "visible"
        decrypted = security.decrypt_strategic_data(encrypted)
        assert decrypted["strategy"] == "expand_to_market_x"

    def test_audit(self):
        security = DecisionSecurityManager()
        entry = security.log_decision("ceo1", "approve_budget", {"amount": 500000})
        assert entry["id"] is not None

    def test_approval_workflow(self):
        security = DecisionSecurityManager()
        needs = security.require_approval("budget", 100000)
        assert needs is True
        needs_small = security.require_approval("budget", 10000)
        assert needs_small is False


class TestDecisionModels:
    def test_kpi(self):
        kpi = KPI(id="kpi-001", name="Receita", value=2500000.0, target=3000000.0, unit="R$")
        assert kpi.value == 2500000.0

    def test_insight(self):
        ins = Insight(id="ins-001", title="Crescimento", description="Vendas subindo",
                      insight_type=InsightType.TREND, severity=AlertSeverity.INFO)
        assert ins.insight_type == InsightType.TREND

    def test_prediction(self):
        pred = Prediction(id="pred-001", metric="revenue", current_value=100.0, predicted_value=115.0, confidence=0.85)
        assert pred.predicted_value == 115.0

    def test_recommendation(self):
        rec = Recommendation(id="rec-001", title="Reduzir custos", description="Cortar 10%",
                             priority=RecommendationPriority.HIGH)
        assert rec.priority == RecommendationPriority.HIGH

    def test_scenario(self):
        s = Scenario(id="sc-001", name="Expansão", scenario_type=ScenarioType.WHAT_IF)
        assert s.status == "draft"

    def test_dashboard(self):
        d = Dashboard(id="dash-001", name="Executivo", dashboard_type=DashboardType.EXECUTIVE)
        assert d.dashboard_type == DashboardType.EXECUTIVE

    def test_alert(self):
        a = Alert(id="alert-001", title="Problema", message="Alerta crítico", severity=AlertSeverity.CRITICAL)
        assert a.severity == AlertSeverity.CRITICAL
        assert a.resolved is False


class TestDashboardManager:
    def test_create_and_list(self):
        dm = DashboardManager(DecisionConfig())
        dash = dm.create_dashboard("Painel Financeiro")
        assert dash.name == "Painel Financeiro"
        all_dash = dm.list_dashboards()
        assert len(all_dash) == 1

    def test_add_widget(self):
        dm = DashboardManager(DecisionConfig())
        dash = dm.create_dashboard("Teste")
        widget = dm.add_widget(dash.id, "Gráfico Vendas")
        assert widget is not None
        assert widget.title == "Gráfico Vendas"


class TestInsightManager:
    def test_create_and_acknowledge(self):
        im = InsightManager()
        ins = im.create_insight("Novo Insight", "Descrição", InsightType.OPPORTUNITY, AlertSeverity.HIGH)
        assert im.acknowledge(ins.id) is True
        assert im.get_active() == []

    def test_get_by_type(self):
        im = InsightManager()
        im.create_insight("T1", "D1", InsightType.TREND)
        im.create_insight("T2", "D2", InsightType.RISK)
        assert len(im.get_by_type(InsightType.TREND)) == 1
        assert len(im.get_by_type(InsightType.RISK)) == 1


class TestStrategyEngine:
    @pytest.mark.asyncio
    async def test_log_decision(self):
        se = StrategyEngine()
        log = await se.log_decision("Expandir mercado", "Oportunidade identificada")
        assert log.decision == "Expandir mercado"

    @pytest.mark.asyncio
    async def test_create_action_plan(self):
        se = StrategyEngine()
        recs = [Recommendation(id="r1", title="Ação 1", description="Desc 1")]
        plan = await se.create_action_plan(recs)
        assert len(plan.recommendations) == 1


class TestSimulationEngineCore:
    @pytest.mark.asyncio
    async def test_execute_scenario(self):
        se = SimulationEngineCore()
        result = await se.execute(Scenario(id="s1", name="Teste", parameters={"investimento": 500000}))
        assert result.feasibility_score > 0
        assert result.confidence > 0


class TestIntegration:
    @pytest.mark.asyncio
    async def test_command_center_flow(self):
        config = DecisionConfig()
        security = DecisionSecurityManager(config)
        engine_config = EngineConfig(config=config, security=security)
        manager_config = ManagerConfig(engine_config=engine_config)
        cc = CommandCenter(manager_config)
        await cc.initialize()

        kpis = await cc.get_kpis()
        assert len(kpis) == 10

        insights = await cc.get_insights()
        assert len(insights) > 0

        predictions = await cc.get_predictions()
        assert len(predictions) > 0

        recs = await cc.get_recommendations()
        assert len(recs) > 0

        health = await cc.get_business_health()
        assert health["health_score"] > 0
        assert health["status"] in ("good", "attention", "critical")

        status = cc.get_engine_status()
        assert status["state"] == "running"

        healthy = cc.is_healthy()
        assert healthy is True

        await cc.shutdown()


if __name__ == "__main__":
    pytest.main(["-v", __file__])
