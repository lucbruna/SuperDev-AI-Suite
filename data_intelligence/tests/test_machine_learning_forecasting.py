"""Tests for the machine learning and forecasting subsystems (Fase 7)."""

from __future__ import annotations

import pytest

from data_intelligence.analytics.prescriptive import PrescriptiveAnalytics
from data_intelligence.data_context import DataIntelligenceContext
from data_intelligence.data_events import DataIntelligenceEvents
from data_intelligence.data_metrics import DataIntelligenceMetrics
from data_intelligence.data_models import ModelStatus
from data_intelligence.machine_learning.base import (MachineLearningError,
                                                     prepare)
from data_intelligence.machine_learning.classification import (
    KNearestNeighborsModel)
from data_intelligence.machine_learning.clustering import KMeansModel
from data_intelligence.machine_learning.engine import MachineLearningEngine
from data_intelligence.machine_learning.evaluation import (
    evaluate_classification, evaluate_regression)
from data_intelligence.machine_learning.recommendation import (
    CollaborativeFilterModel)
from data_intelligence.machine_learning.regression import (
    LinearRegressionModel)
from data_intelligence.forecasting.base import ForecastError
from data_intelligence.forecasting.engine import ForecastingEngine
from data_intelligence.forecasting.exponential import (
    ExponentialSmoothingForecaster)
from data_intelligence.forecasting.moving_average import (
    MovingAverageForecaster)
from data_intelligence.forecasting.naive import (NaiveForecaster,
                                                 SeasonalNaiveForecaster)
from data_intelligence.forecasting.seasonal import SeasonalForecaster


def make_ml_engine() -> MachineLearningEngine:
    return MachineLearningEngine(events=DataIntelligenceEvents(),
                                 metrics=DataIntelligenceMetrics(),
                                 config=None,
                                 context=DataIntelligenceContext())


def make_forecasting_engine() -> ForecastingEngine:
    return ForecastingEngine(metrics=DataIntelligenceMetrics(), config=None,
                             context=DataIntelligenceContext())


# ---------------------------------------------------------------------------
# machine learning: base and models
# ---------------------------------------------------------------------------

def test_prepare_numeric_vectors():
    x_rows, y_values = prepare(
        [{"x": 1, "y": 2, "classe": "a"},
         {"x": 3, "y": 4, "classe": "b"}],
        ["x", "y"], "classe")
    assert x_rows == [[1.0, 2.0], [3.0, 4.0]]
    assert y_values == ["a", "b"]


def test_prepare_non_numeric_raises():
    with pytest.raises(MachineLearningError):
        prepare([{"x": "alto", "y": 1}], ["x", "y"])


def test_linear_regression_exact_fit():
    model = LinearRegressionModel().fit([[1.0], [2.0], [3.0], [4.0]],
                                        [5, 7, 9, 11])
    predictions = model.predict([[5], [0]])
    assert predictions == pytest.approx([13.0, 3.0])


def test_linear_regression_two_features():
    model = LinearRegressionModel().fit(
        [[1.0, 0.0], [2.0, 1.0], [3.0, 2.0], [4.0, 4.0]],
        [5, 11, 17, 27])  # y = 3 + 2*x1 + 4*x2
    assert model.predict([[1.0, 4.0]]) == pytest.approx([21.0])


def test_linear_regression_predict_before_fit_raises():
    with pytest.raises(MachineLearningError):
        LinearRegressionModel().predict([[1]])


def test_knn_classifies_separable_points():
    x_rows = [[1.0, 1.0], [1.0, 2.0], [2.0, 1.0], [10.0, 10.0], [10.0, 11.0],
                                 [11.0, 10.0]]
    y_values = ["a", "a", "a", "b", "b", "b"]
    model = KNearestNeighborsModel(k=3).fit(x_rows, y_values)
    assert model.predict([[1.5, 1.5]]) == ["a"]
    assert model.predict([[10.5, 10.5]]) == ["b"]


def test_knn_confidence():
    x_rows = [[1.0, 1.0], [1.0, 2.0], [2.0, 1.0], [10.0, 10.0], [10.0, 11.0],
                                 [11.0, 10.0]]
    y_values = ["a", "a", "a", "b", "b", "b"]
    model = KNearestNeighborsModel(k=3).fit(x_rows, y_values)
    labels, confidences = model.predict_with_confidence([[1.5, 1.5]])
    assert labels == ["a"]
    assert confidences == [1.0]


def test_knn_predict_before_fit_raises():
    with pytest.raises(MachineLearningError):
        KNearestNeighborsModel().predict([[1.0, 1.0]])


def test_kmeans_two_clusters():
    x_rows = [[0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [10.0, 10.0], [11.0, 10.0],
             [10.0, 11.0]]
    model = KMeansModel(k=2).fit(x_rows)
    groups = model.assignments
    assert groups[0] == groups[2] != groups[3] == groups[5]
    assert model.inertia > 0
    assert model.predict([[9.0, 9.0]]) == [groups[3]]


def test_kmeans_invalid_k_raises():
    with pytest.raises(MachineLearningError):
        KMeansModel(k=10).fit([[1.0], [2.0]])


def test_collaborative_recommendation():
    ratings = {
        "ana": {"cerveja": 5, "pizza": 3},
        "bia": {"cerveja": 4, "pizza": 4, "vinho": 5},
        "carla": {"sushi": 5, "vinho": 4},
    }
    model = CollaborativeFilterModel().fit(ratings)
    top = model.recommend("ana", k=2)
    assert top[0][0] == "vinho"


def test_collaborative_unknown_user_returns_empty():
    model = CollaborativeFilterModel().fit({"a": {"x": 1}})
    assert model.recommend("ghost") == []


# ---------------------------------------------------------------------------
# machine learning: evaluation metrics
# ---------------------------------------------------------------------------

def test_evaluate_regression_perfect_and_noisy():
    metrics = evaluate_regression([5, 7, 9], [5, 7, 9])
    assert metrics["mae"] == 0.0
    assert metrics["r2"] == 1.0
    noisy = evaluate_regression([10, 20], [12, 18])
    assert noisy["mae"] == 2.0
    assert noisy["mse"] == 4.0
    assert noisy["rmse"] == 2.0


def test_evaluate_classification_metrics():
    metrics = evaluate_classification(
        ["a", "a", "b", "b", "b"], ["a", "a", "b", "a", "b"])
    assert metrics["accuracy"] == pytest.approx(0.8)
    assert metrics["precision.a"] == pytest.approx(2 / 3)
    assert metrics["recall.a"] == pytest.approx(1.0)
    assert metrics["f1.b"] == pytest.approx(2 * (2 / 3) * 1.0 / (2 / 3 + 1.0))


def test_evaluate_empty_raises():
    with pytest.raises(ValueError):
        evaluate_regression([], [])
    with pytest.raises(ValueError):
        evaluate_classification([1], [1, 2])


# ---------------------------------------------------------------------------
# machine learning: engine
# ---------------------------------------------------------------------------

def test_ml_engine_train_predict_regression():
    engine = make_ml_engine()
    x_rows = [[1.0], [2.0], [3.0], [4.0]]
    y_values = [5, 7, 9, 11]
    record = engine.train("m1", "Vendas por região", "linear_regression",
                          x_rows, y_values)
    assert record.algorithm == "linear_regression"
    result = engine.predict("m1", {"x": 5})
    assert result.value == pytest.approx(13.0)
    assert result.model_id == "m1"
    assert engine.metrics.snapshot()["counters"]["ml.trained"] == 1


def test_ml_engine_evaluate_updates_confidence():
    engine = make_ml_engine()
    x_rows = [[1.0], [2.0], [3.0], [4.0]]
    y_values = [5, 7, 9, 11]
    engine.train("m1", "Vendas", "linear_regression", x_rows, y_values)
    metrics = engine.evaluate("m1", x_rows, y_values)
    assert metrics["r2"] == pytest.approx(1.0)
    assert engine.records["m1"].status == ModelStatus.EVALUATED
    result = engine.predict("m1", {"x": 5})
    assert result.confidence == pytest.approx(1.0)


def test_ml_engine_knn_predict_with_confidence():
    engine = make_ml_engine()
    x_rows = [[1.0, 1.0], [1.0, 2.0], [2.0, 1.0], [10.0, 10.0], [10.0, 11.0],
                                 [11.0, 10.0]]
    y_values = ["a", "a", "a", "b", "b", "b"]
    engine.train("k1", "Segmento", "knn", x_rows, y_values, k=3)
    result = engine.predict("k1", {"x": 1.5, "y": 1.5})
    assert result.value == "a"
    assert result.confidence == 1.0


def test_ml_engine_clustering_predict():
    engine = make_ml_engine()
    x_rows = [[0.0, 0.0], [1.0, 0.0], [10.0, 10.0], [11.0, 10.0]]
    engine.train("c1", "Grupos", "kmeans", x_rows, k=2)
    result = engine.predict("c1", {"x": 10.5, "y": 10.0})
    assert result.value == engine.models["c1"].predict([[10.5, 10.0]])[0]


def test_ml_engine_collaborative_predict():
    engine = make_ml_engine()
    ratings = {
        "ana": {"cerveja": 5, "pizza": 3},
        "bia": {"cerveja": 4, "pizza": 4, "vinho": 5},
        "carla": {"sushi": 5, "vinho": 4},
    }
    engine.train("r1", "Recomendador", "collaborative", ratings)
    result = engine.predict("r1", {"user": "ana", "k": 1})
    assert result.value[0][0] == "vinho"


def test_ml_engine_unknown_algorithm_raises():
    engine = make_ml_engine()
    with pytest.raises(MachineLearningError):
        engine.train("x", "X", "neural_network", [[1]], [1])


def test_ml_engine_unknown_model_raises():
    engine = make_ml_engine()
    with pytest.raises(MachineLearningError):
        engine.predict("ghost", {"x": 1})
    with pytest.raises(MachineLearningError):
        engine.evaluate("ghost", [[1]], [1])


def test_ml_engine_evaluate_kmeans_raises():
    engine = make_ml_engine()
    engine.train("c1", "Grupos", "kmeans", [[0.0, 0.0], [10.0, 10.0]], k=2)
    with pytest.raises(MachineLearningError):
        engine.evaluate("c1", [[0, 0]], [1])


def test_ml_engine_remove_and_stats():
    engine = make_ml_engine()
    engine.train("m1", "Vendas", "linear_regression", [[1.0], [2.0]],
                 [3.0, 5.0])
    engine.train("k1", "Segmento", "knn", [[0.0], [1.0]], ["a", "b"])
    stats = engine.stats()
    assert stats["models"] == ["k1", "m1"]
    assert engine.remove("m1")
    assert not engine.remove("m1")
    assert engine.stats()["models"] == ["k1"]


def test_ml_engine_feature_model():
    """Modelo com clima e promoção: vendas = 50 + 10*promo + 5*temp."""
    engine = make_ml_engine()
    x_rows = [[0, 20], [1, 20], [0, 30], [1, 30]]
    y_values = [150, 160, 200, 210]
    engine.train("f1", "Vendas com clima", "linear_regression", x_rows,
                 y_values)
    result = engine.predict("f1", {"promo": 1, "temp": 20})
    assert result.value == pytest.approx(160.0)


# ---------------------------------------------------------------------------
# forecasting: forecasters
# ---------------------------------------------------------------------------

def test_naive_forecaster():
    assert NaiveForecaster().fit([10, 20, 30]).forecast(2) == [30.0, 30.0]


def test_naive_empty_raises():
    with pytest.raises(ForecastError):
        NaiveForecaster().fit([])


def test_seasonal_naive_forecaster():
    forecaster = SeasonalNaiveForecaster(season=3).fit([1, 2, 3, 4, 5, 6])
    assert forecaster.forecast(2) == [4.0, 5.0]


def test_seasonal_naive_short_series_raises():
    with pytest.raises(ForecastError):
        SeasonalNaiveForecaster(season=12).fit([1, 2, 3])


def test_moving_average_forecaster():
    forecaster = MovingAverageForecaster(window=3).fit([10, 20, 30])
    assert forecaster.forecast(1) == [20.0]
    assert forecaster.forecast(2) == pytest.approx([20.0, 70 / 3])


def test_exponential_smoothing_forecaster():
    forecaster = ExponentialSmoothingForecaster(alpha=0.5).fit([10, 20])
    assert forecaster.forecast(2) == [15.0, 15.0]


def test_seasonal_forecaster_factors():
    history = {"2024-01": 100, "2024-02": 135, "2024-03": 100,
               "2025-01": 100, "2025-02": 135, "2025-03": 100}
    forecaster = SeasonalForecaster().fit(history)
    assert forecaster.factors["02"] == pytest.approx(
        135 / (670 / 6), rel=1e-6)
    forecast = forecaster.forecast(1, period_key="2026-02")
    assert forecast[0] == pytest.approx(135.0)


def test_seasonal_forecaster_empty_raises():
    with pytest.raises(ForecastError):
        SeasonalForecaster().fit({})


# ---------------------------------------------------------------------------
# forecasting: engine
# ---------------------------------------------------------------------------

def test_forecasting_engine_store_series():
    engine = make_forecasting_engine()
    count = engine.store_series("s1", [
        {"period": "2025-01", "value": 10},
        {"period": "2025-02", "value": 20}])
    assert count == 2
    with pytest.raises(ForecastError):
        engine.store_series("s2", [])
    with pytest.raises(ForecastError):
        engine.store_series("s3", [{"period": "x"}])


def test_forecasting_engine_naive():
    engine = make_forecasting_engine()
    engine.store_series("s1", [{"period": f"p{i}", "value": v}
                               for i, v in enumerate([10, 20, 30])])
    result = engine.forecast("s1", method="naive", horizon=2)
    assert result["forecast"] == [30.0, 30.0]
    assert result["method"] == "naive"


def test_forecasting_engine_moving_average():
    engine = make_forecasting_engine()
    engine.store_series("s1", [{"period": f"p{i}", "value": v}
                               for i, v in enumerate([10, 20, 30])])
    result = engine.forecast("s1", method="moving_average", horizon=1)
    assert result["forecast"] == pytest.approx([20.0])


def test_forecasting_engine_unknown_series():
    engine = make_forecasting_engine()
    with pytest.raises(ForecastError):
        engine.forecast("ghost", method="naive")


def test_forecasting_engine_unknown_method():
    engine = make_forecasting_engine()
    engine.store_series("s1", [{"period": "p1", "value": 1}])
    with pytest.raises(ForecastError):
        engine.forecast("s1", method="fourier")


def test_forecasting_engine_bad_horizon():
    engine = make_forecasting_engine()
    engine.store_series("s1", [{"period": "p1", "value": 1}])
    with pytest.raises(ForecastError):
        engine.forecast("s1", horizon=0)


def test_forecasting_engine_evaluate_mape_and_confidence():
    engine = make_forecasting_engine()
    engine.store_series("s1", [{"period": f"p{i}", "value": v}
                               for i, v in enumerate(range(1, 11))])
    result = engine.evaluate("s1", method="naive", train_ratio=0.5)
    assert result["mae"] == pytest.approx(3.0)
    assert result["mape"] == pytest.approx(
        100 * (1 / 6 + 2 / 7 + 3 / 8 + 4 / 9 + 5 / 10) / 5)
    forecast = engine.forecast("s1", method="naive")
    assert forecast["confidence"] == pytest.approx(
        1.0 - result["mape"] / 100.0)


def test_forecasting_engine_stats():
    engine = make_forecasting_engine()
    engine.store_series("s1", [{"period": "p1", "value": 1}])
    engine.forecast("s1", method="naive")
    stats = engine.stats()
    assert stats["series"] == ["s1"]
    assert "naive" in stats["methods"]
    assert engine.metrics.snapshot()["counters"]["forecasting.forecasts"] == 1


# ---------------------------------------------------------------------------
# real example: supermercado e o carnaval
# ---------------------------------------------------------------------------

def test_real_example_carnaval_plus_35_percent():
    """3 anos de vendas de bebidas: fevereiro (carnaval) 35% acima dos
    demais meses -> previsão de +35% e recomendação de aumentar estoque."""
    engine = make_forecasting_engine()
    points = []
    for year in (2023, 2024, 2025):
        for month in range(1, 13):
            value = 135 if month == 2 else 100
            points.append({"period": f"{year}-{month:02d}",
                           "value": value,
                           "regiao": "sudeste",
                           "clima": "quente",
                           "promocao": month == 2})
    engine.store_series("bebidas", points)

    forecast = engine.forecast("bebidas", method="seasonal",
                               period="2026-02")
    valor = forecast["forecast"][0]
    assert valor == pytest.approx(135.0, rel=1e-6)

    media_mes_normal = 100
    crescimento = round((valor - media_mes_normal) / media_mes_normal * 100)
    assert crescimento == 35

    prescriptive = PrescriptiveAnalytics()
    gap = prescriptive.compute("gap_to_target",
                               [{"current": 100, "target": valor}])
    assert gap["value"] == pytest.approx(-35.0)
    adjustment = gap["detail"]["adjustment"]
    assert adjustment.startswith("increase by 35")
    assert "35" in adjustment
