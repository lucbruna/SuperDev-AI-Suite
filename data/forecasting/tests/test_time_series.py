from __future__ import annotations

import pytest

from SuperDev.data.data_engine import DataEngine
from SuperDev.data.forecasting.time_series import TimeSeriesAnalyzer


class TestSmoothing:
    def test_moving_average_short(self) -> None:
        analyzer = TimeSeriesAnalyzer()
        # window clamped to series length
        assert analyzer.moving_average([1.0, 3.0], window=3) == [1.0, 2.0]

    def test_moving_average_long(self) -> None:
        analyzer = TimeSeriesAnalyzer()
        result = analyzer.moving_average([1.0, 2.0, 3.0, 4.0, 5.0], window=3)
        assert result == pytest.approx([1.0, 1.5, 2.0, 3.0, 4.0])

    def test_moving_average_empty(self) -> None:
        assert TimeSeriesAnalyzer().moving_average([]) == []

    def test_exponential_smoothing(self) -> None:
        analyzer = TimeSeriesAnalyzer()
        result = analyzer.exponential_smoothing([10.0, 20.0, 30.0], alpha=0.5)
        assert result[0] == 10.0
        assert result[-1] > 20.0  # smooths toward the recent value

    def test_exponential_smoothing_alpha_clamped(self) -> None:
        analyzer = TimeSeriesAnalyzer()
        # alpha=2.0 is clamped to 1.0 → pure follow
        assert analyzer.exponential_smoothing([1.0, 5.0], alpha=2.0) == [1.0, 5.0]


class TestDetrending:
    def test_first_differences(self) -> None:
        assert TimeSeriesAnalyzer().first_differences([1.0, 3.0, 6.0]) == [2.0, 3.0]

    def test_first_differences_short(self) -> None:
        assert TimeSeriesAnalyzer().first_differences([1.0]) == []

    def test_detrend_linear_series(self) -> None:
        analyzer = TimeSeriesAnalyzer()
        # perfect linear trend → residual near zero
        detrended = analyzer.detrend([2.0, 4.0, 6.0, 8.0])
        assert all(abs(v) < 1e-6 for v in detrended)

    def test_stationarity_check(self) -> None:
        analyzer = TimeSeriesAnalyzer()
        # random walk has increasing variance → likely non-stationary
        result = analyzer.stationarity_check([1.0, 2.0, 4.0, 8.0, 16.0])
        assert "stationary" in result
        assert "variance" in result and "differenced_variance" in result

    def test_stationarity_check_short(self) -> None:
        result = TimeSeriesAnalyzer().stationarity_check([1.0, 2.0])
        assert result["stationary"] is False


class TestSeasonality:
    def test_seasonal_decompose_shapes(self) -> None:
        analyzer = TimeSeriesAnalyzer()
        series = [10.0, 20.0, 10.0, 20.0, 10.0, 20.0, 10.0, 20.0]
        components = analyzer.seasonal_decompose(series, period=2)
        assert set(components) == {"trend", "seasonal", "residual"}
        assert all(len(v) == len(series) for v in components.values())

    def test_seasonality_strength_strong(self) -> None:
        analyzer = TimeSeriesAnalyzer()
        series = [10.0, 20.0, 10.0, 20.0, 10.0, 20.0, 10.0, 20.0]
        strength = analyzer.seasonality_strength(series, period=2)
        assert strength > 0.5

    def test_seasonality_strength_weak(self) -> None:
        analyzer = TimeSeriesAnalyzer()
        series = [5.0, 5.1, 4.9, 5.0, 5.1, 5.0, 4.9, 5.1]
        strength = analyzer.seasonality_strength(series, period=2)
        # Weak seasonal pattern → strength at most 0.5
        assert strength <= 0.5

    def test_seasonality_strength_insufficient(self) -> None:
        assert TimeSeriesAnalyzer().seasonality_strength([1.0, 2.0], period=2) == 0.0


class TestAutocorrelation:
    def test_perfect_positive(self) -> None:
        analyzer = TimeSeriesAnalyzer()
        assert analyzer.autocorrelation([1.0, 2.0, 3.0, 4.0, 5.0], lag=1) == pytest.approx(1.0, abs=0.01)

    def test_autocorrelation_short(self) -> None:
        assert TimeSeriesAnalyzer().autocorrelation([1.0], lag=1) == 0.0


class TestErrorMetrics:
    def test_mae(self) -> None:
        analyzer = TimeSeriesAnalyzer()
        assert analyzer.mae([1.0, 2.0], [1.5, 2.5]) == 0.5

    def test_rmse(self) -> None:
        analyzer = TimeSeriesAnalyzer()
        # sqrt((9 + 16) / 2) = sqrt(12.5) ≈ 3.5355
        assert analyzer.rmse([0.0, 0.0], [3.0, 4.0]) == pytest.approx(3.5355, abs=1e-3)

    def test_metrics_mismatched_length(self) -> None:
        analyzer = TimeSeriesAnalyzer()
        assert analyzer.mae([1.0], [1.0, 2.0]) == 0.0
        assert analyzer.rmse([1.0], [1.0, 2.0]) == 0.0


class TestAnalyze:
    def test_analyze_full_report(self) -> None:
        analyzer = TimeSeriesAnalyzer()
        report = analyzer.analyze([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0])
        assert report["length"] == 8
        assert report["mean"] == pytest.approx(4.5)
        assert report["trend"] == "increasing"
        assert "stationarity" in report and "seasonality_strength" in report

    def test_analyze_history(self) -> None:
        analyzer = TimeSeriesAnalyzer()
        analyzer.analyze([1.0, 2.0, 3.0])
        analyzer.analyze([5.0, 5.0, 5.0])
        assert len(analyzer.history()) == 2

    def test_analyze_with_engine(self, engine: DataEngine) -> None:
        analyzer = TimeSeriesAnalyzer(engine=engine)
        analyzer.analyze([1.0, 2.0, 3.0])
        assert engine.metrics.get_counter("forecasting.analyses") >= 1
