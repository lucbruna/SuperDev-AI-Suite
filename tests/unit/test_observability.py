"""Unit tests for observability package — logging, metrics, tracing."""

import threading
import time

import pytest

from backend.observability.logging import get_logger, setup_logging
from backend.observability.metrics import MetricsCollector, get_metrics_collector
from backend.observability.tracing import (
    Span,
    SpanStatus,
    Tracer,
    get_current_trace_id,
    get_current_span_id,
    get_tracer,
)


# ── Logging Tests ────────────────────────────────────────────────


class TestSetupLogging:
    def test_setup_json_output(self):
        setup_logging(level="INFO", json_output=True)

    def test_setup_console_output(self):
        setup_logging(level="DEBUG", json_output=False)

    def test_setup_different_levels(self):
        for level in ("DEBUG", "INFO", "WARNING", "ERROR"):
            setup_logging(level=level, json_output=False)


class TestGetLogger:
    def test_returns_logger(self):
        logger = get_logger("test_module")
        assert logger is not None

    def test_default_logger(self):
        logger = get_logger()
        assert logger is not None

    def test_logger_has_name(self):
        logger = get_logger("my.module")
        assert logger is not None


# ── Metrics Tests ────────────────────────────────────────────────


class TestMetricsCollector:
    def test_record_request(self):
        mc = MetricsCollector()
        mc.record_request("GET", "/api/v1/users", 200, 0.05)
        mc.record_request("POST", "/api/v1/users", 201, 0.12)
        mc.record_request("GET", "/api/v1/users", 500, 0.01)

        metrics = mc.get_metrics()
        assert metrics["total_requests"] == 3
        assert metrics["total_errors"] >= 1

    def test_record_error(self):
        mc = MetricsCollector()
        mc.record_error("/api/v1/users", "TimeoutError")
        mc.record_error("/api/v1/users", "TimeoutError")

        metrics = mc.get_metrics()
        assert "/api/v1/users TimeoutError" in metrics["errors"]
        assert metrics["errors"]["/api/v1/users TimeoutError"] == 2

    def test_increment_counter(self):
        mc = MetricsCollector()
        mc.increment_counter("cache.hit")
        mc.increment_counter("cache.hit")
        mc.increment_counter("cache.miss")

        metrics = mc.get_metrics()
        assert metrics["custom_counters"]["cache.hit"] == 2
        assert metrics["custom_counters"]["cache.miss"] == 1

    def test_duration_tracking(self):
        mc = MetricsCollector()
        mc.record_request("GET", "/api", 200, 0.010)
        mc.record_request("GET", "/api", 200, 0.020)
        mc.record_request("GET", "/api", 200, 0.030)

        metrics = mc.get_metrics()
        durations = metrics["durations"]["GET /api"]
        assert durations["count"] == 3
        assert durations["min_ms"] == 10.0
        assert durations["max_ms"] == 30.0
        assert durations["avg_ms"] == 20.0

    def test_error_rate_calculation(self):
        mc = MetricsCollector()
        for _ in range(8):
            mc.record_request("GET", "/ok", 200, 0.01)
        for _ in range(2):
            mc.record_request("GET", "/err", 500, 0.01)

        metrics = mc.get_metrics()
        assert metrics["total_requests"] == 10
        assert metrics["error_rate_pct"] == 20.0

    def test_reset(self):
        mc = MetricsCollector()
        mc.record_request("GET", "/", 200, 0.01)
        mc.reset()

        metrics = mc.get_metrics()
        assert metrics["total_requests"] == 0

    def test_thread_safety(self):
        mc = MetricsCollector()

        def increment():
            for _ in range(100):
                mc.record_request("GET", "/concurrent", 200, 0.01)
                mc.increment_counter("thread.test")

        threads = [threading.Thread(target=increment) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        metrics = mc.get_metrics()
        assert metrics["total_requests"] == 1000
        assert metrics["custom_counters"]["thread.test"] == 1000


class TestMetricsSingleton:
    def test_get_metrics_collector_returns_same_instance(self):
        mc1 = get_metrics_collector()
        mc2 = get_metrics_collector()
        assert mc1 is mc2


# ── Tracing Tests ────────────────────────────────────────────────


class TestSpan:
    def test_span_creation(self):
        span = Span(trace_id="trace-123", name="test.span")
        assert span.trace_id == "trace-123"
        assert span.name == "test.span"
        assert span.status == SpanStatus.UNSET
        assert span.end_time is None
        assert span.duration_ms is None

    def test_span_with_parent(self):
        parent = Span(trace_id="trace-1", name="parent")
        child = Span(trace_id="trace-1", parent_id=parent.span_id, name="child")
        assert child.trace_id == parent.trace_id
        assert child.parent_id == parent.span_id

    def test_span_duration(self):
        span = Span(trace_id="t1", name="timed")
        span.start_time = time.time() - 1.0
        span.end_time = time.time()
        assert span.duration_ms is not None
        assert span.duration_ms >= 900  # ~1 second

    def test_span_to_dict(self):
        span = Span(trace_id="t1", name="export.test")
        d = span.to_dict()
        assert d["trace_id"] == "t1"
        assert d["name"] == "export.test"
        assert "span_id" in d
        assert "status" in d


class TestTracer:
    def test_start_span(self):
        tracer = Tracer()
        span = tracer.start_span("test.op")
        assert span.name == "test.op"
        assert len(span.trace_id) == 32  # UUID hex

    def test_start_span_with_parent(self):
        tracer = Tracer()
        parent = tracer.start_span("parent")
        child = tracer.start_span("child", parent=parent)
        assert child.parent_id == parent.span_id
        assert child.trace_id == parent.trace_id

    def test_end_span(self):
        tracer = Tracer()
        span = tracer.start_span("op")
        tracer.end_span(span, SpanStatus.OK)
        assert span.end_time is not None
        assert span.status == SpanStatus.OK

    def test_inject_headers(self):
        tracer = Tracer()
        span = tracer.start_span("http.call")
        headers = tracer.inject_headers(span)
        assert "X-Trace-ID" in headers
        assert "X-Span-ID" in headers

    def test_extract_headers(self):
        tracer = Tracer()
        headers = {"X-Trace-ID": "abc123", "X-Span-ID": "def456"}
        trace_id, span_id = tracer.extract_headers(headers)
        assert trace_id == "abc123"
        assert span_id == "def456"

    def test_recent_traces(self):
        tracer = Tracer()
        tracer.clear_traces()
        for i in range(5):
            span = tracer.start_span(f"op.{i}")
            tracer.end_span(span)

        traces = tracer.get_recent_traces()
        assert len(traces) == 5
        assert traces[-1]["name"] == "op.4"

    def test_clear_traces(self):
        tracer = Tracer()
        span = tracer.start_span("to.clear")
        tracer.end_span(span)
        tracer.clear_traces()
        assert len(tracer.get_recent_traces()) == 0


class TestTracerSingleton:
    def test_get_tracer_returns_same_instance(self):
        t1 = get_tracer()
        t2 = get_tracer()
        assert t1 is t2


class TestContextVariables:
    def test_get_current_trace_id_default(self):
        result = get_current_trace_id()
        assert result is None or isinstance(result, str)
