from __future__ import annotations

import pytest

from SuperDev.monitoring.tracing.tracer import Tracer
from SuperDev.monitoring.tracing.span import SpanManager
from SuperDev.monitoring.tracing.trace_context import TraceContext
from SuperDev.monitoring.tracing.trace_exporter import ConsoleTraceExporter
from SuperDev.monitoring.tracing.sampling import AlwaysOnSampler, RateSampler
from SuperDev.monitoring.tracing.propagation import W3CPropagator
from SuperDev.monitoring.tracing.visualizer import TraceVisualizer


class TestTracer:
    def test_trace_creation(self) -> None:
        tracer = Tracer()
        span = tracer.start_span("test")
        assert span.span_id is not None
        tracer.end_span(span)

    def test_in_span(self) -> None:
        tracer = Tracer()
        with tracer.in_span("test") as span:
            assert span is not None


class TestSpanManager:
    def test_span_lifecycle(self) -> None:
        mgr = SpanManager(trace_id="t1", span_id="s1")
        child = mgr.start_span("child")
        assert child.parent_id == "s1"


class TestTraceContext:
    def test_context(self) -> None:
        ctx = TraceContext()
        ctx.set("key", "val")
        assert ctx.get("key") == "val"


class TestExporters:
    def test_console_exporter(self) -> None:
        exp = ConsoleTraceExporter()
        exp.export([])  # should not raise


class TestSamplers:
    def test_always_on(self) -> None:
        s = AlwaysOnSampler()
        assert s.should_sample([])

    def test_rate_sampler(self) -> None:
        s = RateSampler(rate=1.0)
        assert s.should_sample([])


class TestPropagator:
    def test_w3c(self) -> None:
        p = W3CPropagator()
        headers = p.inject(trace_id="t1", span_id="s1")
        assert "traceparent" in headers


class TestVisualizer:
    def test_text_visualization(self) -> None:
        v = TraceVisualizer()
        spans = [{"span_id": "s1", "trace_id": "t1", "name": "test", "parent_id": None}]
        text = v.to_text(spans)
        assert "test" in text
