from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import Any

from ..monitoring_models import Span


class Propagator(ABC):
    """Abstract base for context propagators."""

    @abstractmethod
    def inject(self, span: Span, carrier: dict[str, Any]) -> None: ...

    @abstractmethod
    def extract(self, carrier: dict[str, Any]) -> dict[str, str]: ...


class W3CTraceContextPropagator(Propagator):
    """W3C Trace Context propagation (traceparent header)."""

    TRACEPARENT_KEY = "traceparent"
    TRACESTATE_KEY = "tracestate"
    _pattern = re.compile(
        r"^([0-9a-f]{2})-([0-9a-f]{32})-([0-9a-f]{16})-([0-9a-f]{2})$"
    )

    def inject(self, span: Span, carrier: dict[str, Any]) -> None:
        version = "00"
        trace_flags = "01"
        carrier[self.TRACEPARENT_KEY] = (
            f"{version}-{span.trace_id}-{span.span_id}-{trace_flags}"
        )

    def extract(self, carrier: dict[str, Any]) -> dict[str, str]:
        traceparent = carrier.get(self.TRACEPARENT_KEY, "")
        match = self._pattern.match(traceparent)
        if match:
            return {
                "trace_id": match.group(2),
                "span_id": match.group(3),
                "trace_flags": match.group(4),
            }
        return {}


class DatadogPropagator(Propagator):
    """Datadog-style propagation (x-datadog-* headers)."""

    def inject(self, span: Span, carrier: dict[str, Any]) -> None:
        carrier["x-datadog-trace-id"] = str(
            int(span.trace_id[:16], 16) if span.trace_id else 0
        )
        carrier["x-datadog-parent-id"] = str(
            int(span.span_id, 16) if span.span_id else 0
        )

    def extract(self, carrier: dict[str, Any]) -> dict[str, str]:
        trace_id = carrier.get("x-datadog-trace-id", "")
        span_id = carrier.get("x-datadog-parent-id", "")
        return {
            "trace_id": trace_id,
            "span_id": span_id,
        }


class CompositePropagator(Propagator):
    """Tries multiple propagators in sequence."""

    def __init__(self, propagators: list[Propagator]) -> None:
        self._propagators = propagators

    def inject(self, span: Span, carrier: dict[str, Any]) -> None:
        for propagator in self._propagators:
            propagator.inject(span, carrier)

    def extract(self, carrier: dict[str, Any]) -> dict[str, str]:
        for propagator in self._propagators:
            result = propagator.extract(carrier)
            if result:
                return result
        return {}
