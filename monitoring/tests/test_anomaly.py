from __future__ import annotations

import pytest

from SuperDev.monitoring.anomaly.detector import AnomalyDetector
from SuperDev.monitoring.anomaly.statistical import StatisticalDetector
from SuperDev.monitoring.anomaly.ml import MlDetector
from SuperDev.monitoring.anomaly.threshold import ThresholdDetector
from SuperDev.monitoring.anomaly.seasonal import SeasonalDetector
from SuperDev.monitoring.anomaly.correlation import CorrelationDetector


class TestAnomalyDetector:
    def test_detect(self) -> None:
        detector = AnomalyDetector()
        result = detector.detect(50.0, "cpu")
        assert result is not None


class TestStatisticalDetector:
    def test_zscore(self) -> None:
        detector = StatisticalDetector(method="zscore", threshold=3.0)
        values = [10, 11, 10.5, 100, 10, 10.2, 9.8, 10.1]
        for v in values:
            detector.record(v)
        result = detector.detect(100.0)
        assert result.is_anomaly is True


class TestMlDetector:
    def test_moving_average(self) -> None:
        detector = MlDetector(method="moving_average", window=3)
        detector.record(10)
        detector.record(11)
        detector.record(10)
        result = detector.detect(100.0)
        assert result.is_anomaly is True


class TestThresholdDetector:
    def test_fixed_threshold(self) -> None:
        detector = ThresholdDetector(threshold_type="fixed", min=0, max=100)
        assert detector.detect(150).is_anomaly
        assert not detector.detect(50).is_anomaly


class TestSeasonalDetector:
    def test_seasonal(self) -> None:
        detector = SeasonalDetector(window=3)
        for v in [10, 20, 10, 20, 10]:
            detector.record(v)
        result = detector.detect(100.0)
        assert result.is_anomaly is True


class TestCorrelationDetector:
    def test_correlation(self) -> None:
        detector = CorrelationDetector()
        metrics = {"cpu": [10, 20, 30], "mem": [100, 200, 300]}
        result = detector.analyze(metrics)
        assert "cpu_mem" in result
