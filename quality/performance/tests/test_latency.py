"""Tests for the LatencyAnalyzer deep-dive module."""

from __future__ import annotations

import pytest

from SuperDev.quality.performance import LatencyAnalyzer, percentile, time_operation


class TestPercentile:
    def test_nearest_rank(self) -> None:
        values = list(range(1, 101))
        assert percentile(values, 50) == 50
        assert percentile(values, 95) == 95
        assert percentile(values, 99) == 99

    def test_empty(self) -> None:
        assert percentile([], 50) == 0.0


class TestTimeOperation:
    def test_returns_ms(self) -> None:
        duration = time_operation(lambda: None)
        assert duration >= 0.0


class TestLatencyAnalyzer:
    def test_record_and_stats(self) -> None:
        analyzer = LatencyAnalyzer(target_ms=200.0)
        for value in (100.0, 150.0, 200.0, 300.0, 500.0):
            analyzer.record(value)
        stats = analyzer.summary()
        assert stats["samples"] == 5
        assert stats["avg_ms"] == pytest.approx(250.0, abs=0.01)
        assert stats["min_ms"] == 100.0
        assert stats["max_ms"] == 500.0
        assert stats["p50_ms"] == 200.0
        assert stats["jitter"] == pytest.approx(1.6, abs=0.001)

    def test_p95_p99(self) -> None:
        analyzer = LatencyAnalyzer()
        analyzer.record(10.0)
        analyzer.record(20.0)
        analyzer.record(30.0)
        assert analyzer.p50() == 20.0
        assert analyzer.p95() == 30.0
        assert analyzer.p99() == 30.0

    def test_single_sample_jitter_zero(self) -> None:
        analyzer = LatencyAnalyzer()
        analyzer.record(50.0)
        assert analyzer.jitter() == 0.0

    def test_run_operation(self) -> None:
        analyzer = LatencyAnalyzer()
        stats = analyzer.run(lambda: None, samples=10)
        assert stats["samples"] == 10
        assert stats["avg_ms"] >= 0.0

    def test_reset(self) -> None:
        analyzer = LatencyAnalyzer()
        analyzer.record(1.0)
        analyzer.reset()
        assert analyzer.count() == 0


class TestVerdict:
    def test_ok(self) -> None:
        analyzer = LatencyAnalyzer(target_ms=200.0)
        analyzer.record(50.0)
        analyzer.record(100.0)
        verdict = analyzer.verdict()
        assert verdict["level"] == "ok"
        assert verdict["within_target"] is True

    def test_warning(self) -> None:
        analyzer = LatencyAnalyzer(target_ms=100.0)
        analyzer.record(60.0)
        analyzer.record(180.0)
        verdict = analyzer.verdict()
        assert verdict["level"] == "warning"
        assert verdict["within_target"] is True

    def test_critical(self) -> None:
        analyzer = LatencyAnalyzer(target_ms=100.0)
        analyzer.record(300.0)
        analyzer.record(320.0)
        verdict = analyzer.verdict()
        assert verdict["level"] == "critical"
        assert verdict["within_target"] is False


class TestEngineWiring:
    def test_wired_in_engine(self, engine) -> None:
        analyzer = engine.performance.latency_analyzer
        assert analyzer.target_ms == engine.config.performance.latency_target_ms
        analyzer.record(10.0)
        analyzer.record(20.0)
        verdict = analyzer.verdict()
        assert verdict["level"] in ("ok", "warning", "critical")
        assert engine.metrics.get_gauge("performance.latency_p50") is not None
        assert engine.metrics.get_counter("performance.latency_verdicts") >= 1
