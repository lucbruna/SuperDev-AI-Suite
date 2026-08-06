"""Tests for the metrics registry (Phase G)."""
from __future__ import annotations

from modules.autonomous_developer.monitoring import MetricsRegistry


class TestMetricsRegistry:
    def test_increment_default(self):
        registry = MetricsRegistry()
        registry.increment("requests")
        assert registry.snapshot().counters == {"requests": 1}

    def test_increment_by(self):
        registry = MetricsRegistry()
        registry.increment("requests", 3)
        assert registry.snapshot().counters["requests"] == 3

    def test_gauge(self):
        registry = MetricsRegistry()
        registry.gauge("temp", 21.5)
        assert registry.snapshot().gauges == {"temp": 21.5}

    def test_gauge_overwrite(self):
        registry = MetricsRegistry()
        registry.gauge("t", 1)
        registry.gauge("t", 2)
        assert registry.snapshot().gauges == {"t": 2.0}

    def test_histogram_stats(self):
        registry = MetricsRegistry()
        for value in (1, 2, 3):
            registry.histogram("latency", value)
        hist = registry.snapshot().histograms["latency"]
        assert hist == {"count": 3, "min": 1.0, "max": 3.0, "sum": 6.0, "mean": 2.0}

    def test_clear(self):
        registry = MetricsRegistry()
        registry.increment("a")
        registry.clear()
        assert registry.snapshot().counters == {}

    def test_snapshot_isolation(self):
        registry = MetricsRegistry()
        registry.increment("a")
        snapshot = registry.snapshot()
        snapshot.counters["a"] = 99
        assert registry.snapshot().counters == {"a": 1}

    def test_report_formatting(self):
        registry = MetricsRegistry()
        registry.increment("requests", 3)
        registry.gauge("temp", 1.5)
        registry.histogram("latency", 2)
        text = registry.report()
        assert "counter requests = 3" in text
        assert "gauge temp = 1.5" in text
        assert "histogram latency = count=1 mean=2 min=2 max=2" in text

    def test_report_is_sorted(self):
        registry = MetricsRegistry()
        registry.increment("b")
        registry.increment("a")
        lines = registry.report().splitlines()
        assert lines == sorted(lines)
