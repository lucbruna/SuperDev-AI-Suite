from __future__ import annotations

import contextlib
import datetime
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Iterator

from ..monitoring_models import Span, SpanStatus, Trace


@dataclass
class TracerConfig:
    service_name: str = "superdev"
    environment: str = "development"
    sample_rate: float = 1.0
    max_spans_per_trace: int = 1000
    collect_stack_trace: bool = False
    tags: dict[str, str] = field(default_factory=dict)


class Tracer:
    """Distributed tracer that creates and manages spans."""

    def __init__(self, config: TracerConfig | None = None) -> None:
        self._config = config or TracerConfig()
        self._current_trace: Trace | None = None
        self._spans: list[Span] = []
        self._exporters: list[Callable[[Trace], None]] = []

    @property
    def config(self) -> TracerConfig:
        return self._config

    def start_trace(self, operation_name: str, tags: dict[str, str] | None = None) -> Span:
        trace_id = uuid.uuid4().hex
        span = Span(
            span_id=uuid.uuid4().hex[:16],
            trace_id=trace_id,
            operation_name=operation_name,
            tags=tags or {},
        )
        self._current_trace = Trace(
            trace_id=trace_id,
            service_name=self._config.service_name,
        )
        self._spans = [span]
        return span

    def start_span(
        self,
        operation_name: str,
        parent_span_id: str = "",
        tags: dict[str, str] | None = None,
    ) -> Span:
        if not self._current_trace:
            return self.start_trace(operation_name, tags)

        span = Span(
            span_id=uuid.uuid4().hex[:16],
            trace_id=self._current_trace.trace_id,
            parent_span_id=parent_span_id or (self._spans[-1].span_id if self._spans else ""),
            operation_name=operation_name,
            tags=tags or {},
        )
        self._spans.append(span)
        return span

    def end_span(self, span: Span, status: SpanStatus = SpanStatus.OK) -> None:
        span.end_time = time.time()
        span.status = status

    def end_trace(self) -> Trace | None:
        if not self._current_trace:
            return None
        self._current_trace.spans = list(self._spans)
        self._current_trace.end_time = time.time()
        trace = self._current_trace
        self._export(trace)
        self._current_trace = None
        self._spans.clear()
        return trace

    @contextlib.contextmanager
    def in_span(
        self,
        operation_name: str,
        tags: dict[str, str] | None = None,
    ) -> Iterator[Span]:
        span = self.start_span(operation_name, tags=tags)
        try:
            yield span
        except Exception:
            self.end_span(span, SpanStatus.ERROR)
            raise
        else:
            self.end_span(span, SpanStatus.OK)

    def add_exporter(self, exporter: Callable[[Trace], None]) -> None:
        self._exporters.append(exporter)

    def _export(self, trace: Trace) -> None:
        for exporter in self._exporters:
            try:
                exporter(trace)
            except Exception:
                pass

    def get_current_trace(self) -> Trace | None:
        return self._current_trace
