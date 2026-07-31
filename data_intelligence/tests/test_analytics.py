"""Tests for the analytics subsystem (Volume 22, Fase 5)."""

from __future__ import annotations

from data_intelligence.analytics.base import AnalyticsError
from data_intelligence.analytics.engine import AnalyticsEngine
from data_intelligence.analytics.metrics import (average, growth_rate,
                                                 percentage, total)
from data_intelligence.analytics.prescriptive import PrescriptiveAnalytics
from data_intelligence.data_context import DataIntelligenceContext
from data_intelligence.data_events import DataIntelligenceEvents
from data_intelligence.data_metrics import DataIntelligenceMetrics
from data_intelligence.data_models import AnalyticsLevel


def make_engine(**kwargs) -> AnalyticsEngine:
    return AnalyticsEngine(events=DataIntelligenceEvents(),
                           metrics=DataIntelligenceMetrics(), config=None,
                           context=DataIntelligenceContext(), **kwargs)


class TestAnalyticsMetrics:
    def test_total_and_average(self) -> None:
        assert total([10, 20, 30]) == 60
        assert average([10, 20, 30]) == 20
        assert average([]) == 0.0

    def test_growth_rate(self) -> None:
        assert growth_rate(118, 100) == 18.0
        assert growth_rate(0, 100) == -100.0
        assert growth_rate(50, 0) == 100.0

    def test_percentage(self) -> None:
        assert percentage(30, 150) == 20.0
        assert percentage(10, 0) == 0.0


class TestDescriptiveAnalytics:
    def test_total_and_average_metrics(self) -> None:
        engine = make_engine()
        result = engine.compute("total", [{"value": 10}, {"value": 20}])
        assert result["value"] == 30
        assert result["level"] == "descriptive"
        result = engine.compute("average", [{"value": 10}, {"value": 30}])
        assert result["value"] == 20

    def test_growth_vendas_mais_18(self) -> None:
        """Descritiva: vendas +18% (exemplo real do spec)."""
        engine = make_engine()
        data = [{"period": 2024, "value": 100.0},
                {"period": 2025, "value": 118.0}]
        result = engine.compute("growth", data)
        assert result["value"] == 18.0
        assert result["detail"]["latest"] == "2025"

    def test_growth_requires_two_periods(self) -> None:
        engine = make_engine()
        try:
            engine.compute("growth", [{"period": 2024, "value": 100}])
            raised = False
        except AnalyticsError:
            raised = True
        assert raised is True

    def test_distribution(self) -> None:
        from data_intelligence.analytics.descriptive import (
            DescriptiveAnalytics)
        engine = make_engine(descriptive=DescriptiveAnalytics(
            value_field="valor", group_by="uf"))
        result = engine.compute("distribution",
                                [{"uf": "SP", "valor": 10},
                                 {"uf": "SP", "valor": 20},
                                 {"uf": "RJ", "valor": 5}])
        assert result["value"] == {"SP": 30.0, "RJ": 5.0}

    def test_unknown_metric(self) -> None:
        engine = make_engine()
        try:
            engine.compute("nope", [])
            raised = False
        except AnalyticsError:
            raised = True
        assert raised is True


class TestDiagnosticAnalytics:
    def test_compare_regions(self) -> None:
        """Diagnóstica: promoção regional (comparação por região)."""
        engine = make_engine()
        data = [{"group": "norte", "value": 30},
                {"group": "sul", "value": 90},
                {"group": "sul", "value": 90}]
        result = engine.compute("compare", data)
        assert result["level"] == "diagnostic"
        assert result["value"]["sul"] == 180
        assert result["value"]["norte"] == 30
        assert result["detail"]["best"] == "sul"
        assert result["detail"]["worst"] == "norte"
        assert result["detail"]["gap"] == 150

    def test_anomalies(self) -> None:
        engine = make_engine()
        data = [{"value": 10}, {"value": 12}, {"value": 11},
                {"value": 13}, {"value": 12}, {"value": 100}]
        result = engine.compute("anomalies", data)
        assert len(result["value"]) == 1
        assert result["value"][0]["value"] == 100

    def test_compare_no_records(self) -> None:
        engine = make_engine()
        try:
            engine.compute("compare", [])
            raised = False
        except AnalyticsError:
            raised = True
        assert raised is True

    def test_anomalies_small_set(self) -> None:
        engine = make_engine()
        result = engine.compute("anomalies", [{"value": 5}])
        assert result["value"] == []


class TestPredictiveAnalytics:
    def test_trend(self) -> None:
        """Preditiva: tendência linear (vendas crescentes)."""
        engine = make_engine()
        data = [{"period": 1, "value": 10},
                {"period": 2, "value": 20},
                {"period": 3, "value": 30}]
        result = engine.compute("trend", data)
        assert result["level"] == "predictive"
        assert result["value"]["4"] == 40.0

    def test_days_until_stock_out(self) -> None:
        """Preditiva: estoque acaba em 12 dias."""
        engine = make_engine()
        result = engine.compute("days_until",
                                [{"inventory": 120, "daily_demand": 10}])
        assert result["value"] == 12

    def test_run_rate(self) -> None:
        engine = make_engine()
        result = engine.compute(
            "run_rate", [{"current_total": 500, "elapsed_fraction": 0.5}])
        assert result["value"] == 1000.0

    def test_days_until_zero_demand(self) -> None:
        engine = make_engine()
        try:
            engine.compute("days_until", [{"inventory": 10,
                                           "daily_demand": 0}])
            raised = False
        except AnalyticsError:
            raised = True
        assert raised is True

    def test_trend_insufficient_points(self) -> None:
        engine = make_engine()
        try:
            engine.compute("trend", [{"period": 1, "value": 10}])
            raised = False
        except AnalyticsError:
            raised = True
        assert raised is True


class TestPrescriptiveAnalytics:
    def test_recommend(self) -> None:
        """Prescritiva: comprar quando o estoque fica baixo."""
        engine = make_engine(prescriptive=engine_factory())
        result = engine.compute("recommend", [{"estoque": 400}])
        assert result["level"] == "prescriptive"
        assert len(result["value"]) == 1
        assert result["value"][0]["recommendation"] == "comprar 500 unidades"

    def test_recommend_no_match(self) -> None:
        engine = make_engine(prescriptive=engine_factory())
        result = engine.compute("recommend", [{"estoque": 900}])
        assert result["value"] == []

    def test_gap_to_target(self) -> None:
        engine = make_engine()
        result = engine.compute(
            "gap_to_target", [{"current": 100, "target": 92}])
        assert result["value"] == 8.0
        assert "reduce" in result["detail"]["adjustment"]


def engine_factory():
    from data_intelligence.analytics.prescriptive import PrescriptiveAnalytics
    return PrescriptiveAnalytics(rules=[
        {"name": "estoque baixo", "field": "estoque", "op": "lt",
         "value": 500,
         "recommendation": "comprar 500 unidades"},
    ])


class TestAnalyticsEngine:
    def test_routing(self) -> None:
        engine = make_engine()
        assert engine.provider_for("growth")[1] == "descriptive"
        assert engine.provider_for("compare")[1] == "diagnostic"
        assert engine.provider_for("trend")[1] == "predictive"
        assert engine.provider_for("recommend")[1] == "prescriptive"
        assert engine.provider_for("whatever")[1] == "descriptive"

    def test_descriptive_result_model(self) -> None:
        engine = make_engine()
        result = engine.descriptive_result(
            "total", [{"value": 5}, {"value": 5}])
        assert result.level is AnalyticsLevel.DESCRIPTIVE
        assert result.value == 10
        assert result.to_dict()["level"] == "descriptive"

    def test_run_analysis_explicit_level(self) -> None:
        engine = make_engine()
        result = engine.run_analysis(
            AnalyticsLevel.PREDICTIVE, "days_until",
            [{"inventory": 24, "daily_demand": 3}])
        assert result.level is AnalyticsLevel.PREDICTIVE
        assert result.value == 8

    def test_history_and_stats(self) -> None:
        engine = make_engine()
        engine.compute("total", [{"value": 1}])
        engine.compute("compare", [{"group": "a", "value": 1}])
        engine.compute("trend", [{"period": 1, "value": 1},
                                 {"period": 2, "value": 2}])
        stats = engine.stats()
        assert stats["computations"] == 3
        assert stats["levels"]["descriptive"]["computations"] == 1
        assert stats["levels"]["diagnostic"]["computations"] == 1
        assert stats["levels"]["predictive"]["computations"] == 1

    def test_manager_integration(self) -> None:
        from data_intelligence.data_factory import build_engine
        engine = build_engine()
        analytics = AnalyticsEngine(events=engine.events,
                                    metrics=engine.metrics,
                                    config=engine.config,
                                    context=engine.context)
        engine.attach_subsystem("analytics", analytics)
        result = engine.analyze("total", [{"value": 3}, {"value": 4}])
        assert result["value"] == 7
        assert engine.manager.analytics_engine is analytics

    def test_real_example_fluxo(self) -> None:
        """Exemplo completo: vendas caíram 40% -> diagnosticar -> agir."""
        engine = make_engine()
        vendas = [{"period": "antes", "value": 1000.0},
                  {"period": "depois", "value": 600.0}]
        queda = engine.compute("growth", vendas)["value"]
        assert queda == -40.0  # vendas caíram 40%
        causa = engine.compute(
            "compare",
            [{"group": "concorrente", "value": 650},
             {"group": "nosso_produto", "value": 550}])
        assert causa["detail"]["best"] == "concorrente"
        acao = make_engine(prescriptive=engine_factory())
        recomendacao = acao.compute("recommend",
                                    [{"estoque": 400}])["value"]
        assert recomendacao[0]["recommendation"] == "comprar 500 unidades"

    def test_real_example_produto_x(self) -> None:
        """Exemplo completo do Produto X: vendas caíram 40% e preço está
        acima dos concorrentes -> diagnosticar -> agir (reduzir preço 8% +
        campanha digital + promoção)."""
        engine = make_engine()
        vendas = [{"period": "antes", "value": 500.0},
                  {"period": "depois", "value": 300.0}]
        queda = engine.compute("growth", vendas)["value"]
        assert queda == -40.0  # vendas do Produto X caíram 40%

        causa = engine.compute(
            "compare",
            [{"group": "nosso_produto", "value": 12.0},
             {"group": "concorrente", "value": 10.0}])
        assert causa["detail"]["best"] == "nosso_produto"  # preço acima
        assert causa["detail"]["gap"] == 2.0

        prescriptive = PrescriptiveAnalytics(rules=[
            {"name": "preco_acima", "field": "preco", "op": "gt",
             "value": 10.0,
             "recommendation": "reduzir preço em 8% + campanha digital + "
                               "promoção"},
        ])
        acao = prescriptive.compute(
            "recommend", [{"produto": "X", "preco": 12.0}])
        assert len(acao["value"]) == 1
        rec = acao["value"][0]["recommendation"]
        assert "reduzir preço" in rec and "8%" in rec
        assert "campanha digital" in rec and "promoção" in rec
