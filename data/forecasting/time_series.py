from __future__ import annotations

import statistics
from typing import Any


class TimeSeriesAnalyzer:
    """Time series analysis toolkit.

    Provides classic analysis primitives that power the ForecastingEngine:
    smoothing (moving average / exponential), detrending, seasonal
    decomposition, stationarity checks, autocorrelation and error metrics.
    All methods are stdlib-only and operate on plain ``list[float]`` series.
    """

    def __init__(self, engine: Any | None = None) -> None:
        self.engine = engine
        self._analyses: dict[str, dict[str, Any]] = {}

    # -- smoothing -----------------------------------------------------------

    def moving_average(self, series: list[float], window: int = 3) -> list[float]:
        """Simple moving average. Returns a smoothed series of the same length.

        Leading positions (where the window is not yet full) use the partial
        window so the output length matches the input length.
        """
        if not series:
            return []
        window = max(1, min(window, len(series)))
        smoothed: list[float] = []
        for i in range(len(series)):
            chunk = series[max(0, i - window + 1): i + 1]
            smoothed.append(round(statistics.mean(chunk), 4))
        return smoothed

    def exponential_smoothing(self, series: list[float], alpha: float = 0.3) -> list[float]:
        """Single exponential smoothing. ``alpha`` must be in (0, 1]."""
        if not series:
            return []
        alpha = max(0.01, min(1.0, alpha))
        smoothed = [round(series[0], 4)]
        for value in series[1:]:
            smoothed.append(round(alpha * value + (1 - alpha) * smoothed[-1], 4))
        return smoothed

    # -- detrending / stationarity ------------------------------------------

    def first_differences(self, series: list[float]) -> list[float]:
        """First-order differencing, used to remove trends before analysis."""
        if len(series) < 2:
            return []
        return [round(series[i] - series[i - 1], 4) for i in range(1, len(series))]

    def detrend(self, series: list[float]) -> list[float]:
        """Remove a linear trend fit via least squares (centered series)."""
        if len(series) < 2:
            return [round(v, 4) for v in series]
        xs = list(range(len(series)))
        mx = statistics.mean(xs)
        my = statistics.mean(series)
        slope = sum((x - mx) * (y - my) for x, y in zip(xs, series, strict=False)) / max(
            sum((x - mx) ** 2 for x in xs), 1e-9
        )
        intercept = my - slope * mx
        return [round(series[i] - (intercept + slope * i), 4) for i in range(len(series))]

    def stationarity_check(self, series: list[float]) -> dict[str, Any]:
        """Heuristic stationarity: compare variance of raw vs differenced series.

        Returns a dict with ``stationary``, ``variance`` and
        ``differenced_variance``. A series is considered stationary when
        differencing does not meaningfully reduce the variance.
        """
        if len(series) < 3:
            return {"stationary": False, "variance": 0.0, "differenced_variance": 0.0, "note": "insufficient_data"}
        variance = statistics.pstdev(series) ** 2
        differenced = self.first_differences(series)
        diff_variance = statistics.pstdev(differenced) ** 2 if len(differenced) > 1 else variance
        return {
            "stationary": diff_variance >= variance * 0.8,
            "variance": round(variance, 4),
            "differenced_variance": round(diff_variance, 4),
        }

    # -- seasonality ---------------------------------------------------------

    def seasonal_decompose(self, series: list[float], period: int = 4) -> dict[str, list[float]]:
        """Additive seasonal decomposition into trend, seasonal and residual.

        The trend is extracted with a moving average of size ``period``; the
        seasonal component is the per-period average of the detrended series;
        the residual is what remains.
        """
        if not series or period <= 1:
            return {"trend": list(series), "seasonal": [0.0] * len(series), "residual": [0.0] * len(series)}

        trend = self.moving_average(series, window=period)
        detrended = [series[i] - trend[i] for i in range(len(series))]

        seasonal: list[float] = [0.0] * len(series)
        for phase in range(period):
            indices = list(range(phase, len(series), period))
            values = [detrended[i] for i in indices]
            phase_mean = statistics.mean(values) if values else 0.0
            for i in indices:
                seasonal[i] = phase_mean

        residual = [detrended[i] - seasonal[i] for i in range(len(series))]
        return {
            "trend": [round(v, 4) for v in trend],
            "seasonal": [round(v, 4) for v in seasonal],
            "residual": [round(v, 4) for v in residual],
        }

    def seasonality_strength(self, series: list[float], period: int = 4) -> float:
        """Estimate how seasonal a series is (0.0 → 1.0)."""
        if len(series) < period * 2:
            return 0.0
        components = self.seasonal_decompose(series, period)
        residual_var = statistics.pstdev(components["residual"]) ** 2
        total_var = statistics.pstdev(series) ** 2
        if total_var == 0:
            return 0.0
        return round(max(0.0, min(1.0, 1 - residual_var / total_var)), 4)

    # -- autocorrelation -----------------------------------------------------

    def autocorrelation(self, series: list[float], lag: int = 1) -> float:
        """Pearson correlation of the series with itself shifted by ``lag``."""
        if len(series) <= lag:
            return 0.0
        x = series[: len(series) - lag]
        y = series[lag:]
        mx = statistics.mean(x)
        my = statistics.mean(y)
        denom = max(
            sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y),
            1e-9,
        ) ** 0.5
        return round(sum((a - mx) * (b - my) for a, b in zip(x, y, strict=False)) / denom, 4)

    # -- error metrics -------------------------------------------------------

    def mae(self, actual: list[float], predicted: list[float]) -> float:
        """Mean absolute error."""
        if not actual or len(actual) != len(predicted):
            return 0.0
        return round(sum(abs(a - p) for a, p in zip(actual, predicted, strict=False)) / len(actual), 4)

    def rmse(self, actual: list[float], predicted: list[float]) -> float:
        """Root mean squared error."""
        if not actual or len(actual) != len(predicted):
            return 0.0
        return round(
            (sum((a - p) ** 2 for a, p in zip(actual, predicted, strict=False)) / len(actual)) ** 0.5,
            4,
        )

    # -- high-level ----------------------------------------------------------

    def analyze(self, series: list[float], period: int = 4) -> dict[str, Any]:
        """Run the full analysis toolkit and store the result."""
        result = {
            "length": len(series),
            "mean": round(statistics.mean(series), 4) if series else 0.0,
            "stdev": round(statistics.pstdev(series), 4) if series else 0.0,
            "trend": self.trend_direction(series),
            "stationarity": self.stationarity_check(series),
            "seasonality_strength": self.seasonality_strength(series, period),
            "autocorrelation_lag1": self.autocorrelation(series, lag=1),
        }
        analysis_id = f"ts_{len(self._analyses) + 1}"
        self._analyses[analysis_id] = result
        if self.engine is not None:
            self.engine.metrics.increment("forecasting.analyses")
        return result

    def trend_direction(self, series: list[float]) -> str:
        """Classify the dominant trend direction of a series."""
        if len(series) < 2:
            return "flat"
        delta = series[-1] - series[0]
        if delta > 0:
            return "increasing"
        if delta < 0:
            return "decreasing"
        return "flat"

    def history(self) -> dict[str, dict[str, Any]]:
        return dict(self._analyses)


__all__ = ["TimeSeriesAnalyzer"]
