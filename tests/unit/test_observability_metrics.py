"""Tests for observability module: logging, metrics."""

import pytest
from backend.observability.logging import (
    get_logger,
    setup_logging,
    HAS_STRUCTLOG,
)
from backend.observability.metrics import (
    MetricPoint,
    MetricsCollector,
    get_metrics_collector,
)


# ── Logging ─────────────────────────────────────────────────────────


class TestLogging:
    def test_setup_logging_runs(self):
        # Should not raise
        setup_logging(level="INFO", json_output=True)

    def test_setup_logging_console(self):
        setup_logging(level="DEBUG", json_output=False)

    def test_get_logger(self):
        logger = get_logger("test_module")
        assert logger is not None

    def test_get_logger_no_name(self):
        logger = get_logger()
        assert logger is not None


# ── MetricPoint ─────────────────────────────────────────────────────


class TestMetricPoint:
    def test_creation(self):
        point = MetricPoint(name="requests", value=42.0)
        assert point.name == "requests"
        assert point.value == 42.0
        assert point.labels == {}
        assert point.timestamp > 0

    def test_with_labels(self):
        point = MetricPoint(
            name="errors",
            value=5.0,
            labels={"endpoint": "/api/v1/users", "method": "GET"},
        )
        assert point.labels["endpoint"] == "/api/v1/users"


# ── MetricsCollector ────────────────────────────────────────────────


class TestMetricsCollector:
    def test_record_request(self):
        collector = MetricsCollector()
        collector.record_request("GET", "/api/v1/users", 200, 0.05)
        metrics = collector.get_metrics()
        assert metrics["total_requests"] == 1

    def test_record_multiple_requests(self):
        collector = MetricsCollector()
        collector.record_request("GET", "/api/v1/users", 200, 0.05)
        collector.record_request("GET", "/api/v1/users", 200, 0.03)
        collector.record_request("POST", "/api/v1/users", 201, 0.1)
        metrics = collector.get_metrics()
        assert metrics["total_requests"] == 3

    def test_record_error(self):
        collector = MetricsCollector()
        collector.record_request("GET", "/api/v1/users", 500, 0.1)
        metrics = collector.get_metrics()
        assert metrics["total_errors"] >= 1

    def test_record_4xx_not_counted_as_server_error(self):
        collector = MetricsCollector()
        collector.record_request("GET", "/api/v1/users", 404, 0.01)
        metrics = collector.get_metrics()
        # 4xx should not be counted as "server errors" (500+)
        assert metrics["total_errors"] == 0

    def test_record_application_error(self):
        collector = MetricsCollector()
        collector.record_error("/api/v1/users", "TimeoutError")
        metrics = collector.get_metrics()
        assert "TimeoutError" in str(metrics["errors"])

    def test_increment_counter(self):
        collector = MetricsCollector()
        collector.increment_counter("cache_hits")
        collector.increment_counter("cache_hits")
        collector.increment_counter("cache_hits", 5)
        metrics = collector.get_metrics()
        assert metrics["custom_counters"]["cache_hits"] == 7

    def test_get_metrics_durations(self):
        collector = MetricsCollector()
        collector.record_request("GET", "/api", 200, 0.1)
        collector.record_request("GET", "/api", 200, 0.2)
        metrics = collector.get_metrics()
        assert "GET /api" in metrics["durations"]
        dur = metrics["durations"]["GET /api"]
        assert dur["count"] == 2
        assert dur["avg_ms"] == 150.0  # (0.1 + 0.2) / 2 * 1000

    def test_reset(self):
        collector = MetricsCollector()
        collector.record_request("GET", "/api", 200, 0.1)
        collector.increment_counter("test")
        collector.reset()
        metrics = collector.get_metrics()
        assert metrics["total_requests"] == 0
        assert metrics["custom_counters"] == {}

    def test_duration_trim(self):
        collector = MetricsCollector()
        # Add more than 1000 durations
        for i in range(1100):
            collector.record_request("GET", "/api", 200, 0.01)
        metrics = collector.get_metrics()
        # Should be trimmed to 1000
        assert metrics["durations"]["GET /api"]["count"] == 1000


# ── Global singleton ────────────────────────────────────────────────


class TestMetricsSingleton:
    def test_get_metrics_collector(self):
        collector = get_metrics_collector()
        assert isinstance(collector, MetricsCollector)

    def test_singleton_same_instance(self):
        c1 = get_metrics_collector()
        c2 = get_metrics_collector()
        assert c1 is c2
