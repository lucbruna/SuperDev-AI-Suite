"""Lightweight distributed tracing without heavy OpenTelemetry dependencies."""

from __future__ import annotations

import uuid
import time
from collections import deque
from contextvars import ContextVar
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SpanStatus(str, Enum):
    OK = "OK"
    ERROR = "ERROR"
    UNSET = "UNSET"


@dataclass
class Span:
    """A single trace span representing a unit of work."""

    trace_id: str
    span_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    parent_id: str | None = None
    name: str = ""
    start_time: float = field(default_factory=time.time)
    end_time: float | None = None
    status: SpanStatus = SpanStatus.UNSET
    attributes: dict[str, Any] = field(default_factory=dict)

    @property
    def duration_ms(self) -> float | None:
        if self.end_time is None:
            return None
        return round((self.end_time - self.start_time) * 1000, 2)

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_id": self.parent_id,
            "name": self.name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration_ms,
            "status": self.status.value,
            "attributes": self.attributes,
        }


# Context variables for current trace/span
_current_trace_id: ContextVar[str | None] = ContextVar("current_trace_id", default=None)
_current_span_id: ContextVar[str | None] = ContextVar("current_span_id", default=None)

# Recent traces buffer (ring buffer)
_recent_traces: deque[dict[str, Any]] = deque(maxlen=1000)


class Tracer:
    """Lightweight tracer for creating and managing trace spans."""

    def __init__(self, service_name: str = "superdev") -> None:
        self.service_name = service_name

    def start_span(
        self,
        name: str,
        parent: Span | None = None,
        attributes: dict[str, Any] | None = None,
    ) -> Span:
        """Start a new trace span.

        Args:
            name: Span name (e.g., 'auth.login', 'db.query').
            parent: Optional parent span.
            attributes: Optional span attributes.

        Returns:
            A new Span instance.
        """
        trace_id = parent.trace_id if parent else uuid.uuid4().hex
        parent_id = parent.span_id if parent else None

        span = Span(
            trace_id=trace_id,
            parent_id=parent_id,
            name=name,
            attributes=attributes or {},
        )

        # Update context
        _current_trace_id.set(trace_id)
        _current_span_id.set(span.span_id)

        return span

    def end_span(self, span: Span, status: SpanStatus = SpanStatus.OK) -> None:
        """End a trace span and record it.

        Args:
            span: The span to end.
            status: Final status of the span.
        """
        span.end_time = time.time()
        span.status = status

        # Store in recent traces
        _recent_traces.append(span.to_dict())

        # Reset context if this was the root span
        if span.parent_id is None:
            _current_trace_id.set(None)
            _current_span_id.set(None)

    def inject_headers(self, span: Span) -> dict[str, str]:
        """Inject trace context into HTTP headers for distributed tracing."""
        return {
            "X-Trace-ID": span.trace_id,
            "X-Span-ID": span.span_id,
        }

    def extract_headers(self, headers: dict[str, str]) -> tuple[str | None, str | None]:
        """Extract trace context from HTTP headers."""
        trace_id = headers.get("X-Trace-ID")
        span_id = headers.get("X-Span-ID")
        return trace_id, span_id

    def get_recent_traces(self, limit: int = 50) -> list[dict[str, Any]]:
        """Get the most recent traces."""
        traces = list(_recent_traces)
        return traces[-limit:]

    def clear_traces(self) -> None:
        """Clear the trace buffer."""
        _recent_traces.clear()


# Singleton tracer
_tracer: Tracer | None = None
_tracer_lock = __import__("threading").Lock()


def get_tracer(service_name: str = "superdev") -> Tracer:
    """Get or create the global tracer singleton."""
    global _tracer
    if _tracer is None:
        with _tracer_lock:
            if _tracer is None:
                _tracer = Tracer(service_name=service_name)
    return _tracer


def get_current_trace_id() -> str | None:
    """Get the current trace ID from context."""
    return _current_trace_id.get()


def get_current_span_id() -> str | None:
    """Get the current span ID from context."""
    return _current_span_id.get()
