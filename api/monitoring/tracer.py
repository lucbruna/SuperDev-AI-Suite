from __future__ import annotations

import time
import uuid
from typing import Any


class Tracer:
    """Distributed tracing support for API requests."""

    def __init__(self, service_name: str = "api-engine") -> None:
        self._service_name = service_name
        self._spans: dict[str, list[dict[str, Any]]] = {}
        self._traces: dict[str, dict[str, Any]] = {}
        self._sampling_rate: float = 1.0

    def set_sampling_rate(self, rate: float) -> None:
        self._sampling_rate = max(0.0, min(1.0, rate))

    def start_trace(self, trace_id: str | None = None) -> str:
        trace_id = trace_id or str(uuid.uuid4())
        self._traces[trace_id] = {
            "trace_id": trace_id,
            "service": self._service_name,
            "started_at": time.time(),
            "spans": [],
        }
        self._spans[trace_id] = []
        return trace_id

    def start_span(
        self,
        trace_id: str,
        name: str,
        parent_span_id: str | None = None,
    ) -> str:
        span_id = str(uuid.uuid4())
        span: dict[str, Any] = {
            "span_id": span_id,
            "trace_id": trace_id,
            "name": name,
            "parent_span_id": parent_span_id,
            "started_at": time.time(),
            "ended_at": None,
            "duration_ms": None,
            "tags": {},
            "events": [],
        }
        if trace_id in self._spans:
            self._spans[trace_id].append(span)
        return span_id

    def end_span(self, trace_id: str, span_id: str, tags: dict[str, Any] | None = None) -> None:
        spans = self._spans.get(trace_id, [])
        for span in spans:
            if span["span_id"] == span_id:
                span["ended_at"] = time.time()
                span["duration_ms"] = (span["ended_at"] - span["started_at"]) * 1000
                if tags:
                    span["tags"].update(tags)
                break

    def add_span_event(self, trace_id: str, span_id: str, event_name: str, attrs: dict[str, Any] | None = None) -> None:
        spans = self._spans.get(trace_id, [])
        for span in spans:
            if span["span_id"] == span_id:
                span["events"].append({
                    "name": event_name,
                    "timestamp": time.time(),
                    "attributes": attrs or {},
                })
                break

    def get_trace(self, trace_id: str) -> dict[str, Any] | None:
        trace = self._traces.get(trace_id)
        if trace:
            trace["spans"] = self._spans.get(trace_id, [])
            trace["span_count"] = len(trace["spans"])
        return trace

    def to_dict(self) -> dict[str, Any]:
        return {
            "tracer": "DistributedTracer",
            "service": self._service_name,
            "active_traces": len(self._traces),
            "sampling_rate": self._sampling_rate,
        }
