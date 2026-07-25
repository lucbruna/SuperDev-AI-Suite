import uuid
import time
from typing import Dict, List, Optional, Any


class Span:
    def __init__(self, name: str, trace_id: str, parent_id: Optional[str] = None) -> None:
        self.name = name
        self.trace_id = trace_id
        self.span_id = str(uuid.uuid4())
        self.parent_id = parent_id
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.attributes: Dict[str, Any] = {}
        self.status: str = "ok"

    def end(self) -> None:
        self.end_time = time.time()

    def set_attribute(self, key: str, value: Any) -> None:
        self.attributes[key] = value

    def set_status(self, status: str) -> None:
        self.status = status

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_id": self.parent_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "attributes": self.attributes,
            "status": self.status,
        }


class Trace:
    def __init__(self, trace_id: str) -> None:
        self.trace_id = trace_id
        self.spans: List[Span] = []

    def add_span(self, span: Span) -> None:
        self.spans.append(span)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "spans": [s.to_dict() for s in self.spans],
        }


class Tracer:
    def __init__(self, name: str, manager: "TracingManager") -> None:
        self._name = name
        self._manager = manager

    def start_span(self, span_name: str, context: Optional[Dict[str, Any]] = None) -> Span:
        parent_id = (context or {}).get("parent_id")
        trace_id = (context or {}).get("trace_id", str(uuid.uuid4()))
        span = Span(span_name, trace_id, parent_id=parent_id)
        if trace_id not in self._manager._traces:
            self._manager._traces[trace_id] = Trace(trace_id)
        self._manager._traces[trace_id].add_span(span)
        return span


class TracingManager:
    def __init__(self) -> None:
        self._tracers: Dict[str, Tracer] = {}
        self._traces: Dict[str, Trace] = {}

    def tracer(self, name: str) -> Tracer:
        if name not in self._tracers:
            self._tracers[name] = Tracer(name, self)
        return self._tracers[name]

    def start_span(self, name: str, context: Optional[Dict[str, Any]] = None) -> Span:
        tracer = self.tracer("default")
        return tracer.start_span(name, context)

    def end_span(self, span: Span) -> None:
        span.end()

    def get_trace(self, trace_id: str) -> Optional[Trace]:
        return self._traces.get(trace_id)

    def get_all_traces(self) -> Dict[str, Trace]:
        return dict(self._traces)
