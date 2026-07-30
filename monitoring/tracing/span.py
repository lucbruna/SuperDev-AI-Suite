from __future__ import annotations

import time
import uuid
from typing import Any

from ..monitoring_models import Span, SpanStatus


class SpanManager:
    """Manages span lifecycle and relationships."""

    def __init__(self) -> None:
        self._spans: dict[str, Span] = {}

    def create(
        self,
        operation_name: str,
        trace_id: str,
        parent_span_id: str = "",
        tags: dict[str, str] | None = None,
    ) -> Span:
        span = Span(
            span_id=uuid.uuid4().hex[:16],
            trace_id=trace_id,
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            tags=tags or {},
        )
        self._spans[span.span_id] = span
        return span

    def end(self, span_id: str, status: SpanStatus = SpanStatus.OK) -> Span | None:
        span = self._spans.get(span_id)
        if not span:
            return None
        span.end_time = time.time()
        span.status = status
        return span

    def get(self, span_id: str) -> Span | None:
        return self._spans.get(span_id)

    def get_by_trace(self, trace_id: str) -> list[Span]:
        return [s for s in self._spans.values() if s.trace_id == trace_id]

    def add_log(self, span_id: str, log_entry: dict[str, Any]) -> None:
        span = self._spans.get(span_id)
        if span:
            span.logs.append(log_entry)

    def add_tag(self, span_id: str, key: str, value: str) -> None:
        span = self._spans.get(span_id)
        if span:
            span.tags[key] = value

    def clear(self) -> None:
        self._spans.clear()

    @property
    def active_spans(self) -> list[Span]:
        return [s for s in self._spans.values() if s.end_time == 0.0]

    @property
    def all_spans(self) -> list[Span]:
        return list(self._spans.values())
