"""Span management."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time, uuid

class SpanManager:
    def __init__(self) -> None:
        self._active_spans: Dict[str, Dict[str, Any]] = {}
        self._completed: List[Dict[str, Any]] = []
    def start_span(self, name: str, trace_id: str = "", parent_span_id: str = "") -> str:
        span_id = str(uuid.uuid4())[:8]
        if not trace_id:
            trace_id = str(uuid.uuid4())[:8]
        self._active_spans[span_id] = {"span_id": span_id, "trace_id": trace_id, "parent_span_id": parent_span_id, "name": name, "start_time": time.time(), "attributes": {}}
        return span_id
    def end_span(self, span_id: str, status: str = "ok") -> Optional[Dict[str, Any]]:
        span = self._active_spans.pop(span_id, None)
        if not span:
            return None
        span["end_time"] = time.time()
        span["duration_ms"] = (span["end_time"] - span["start_time"]) * 1000
        span["status"] = status
        self._completed.append(span)
        return span
    def get_span(self, span_id: str) -> Optional[Dict[str, Any]]:
        if span_id in self._active_spans:
            return self._active_spans[span_id]
        for s in self._completed:
            if s["span_id"] == span_id:
                return s
        return None
    def active_count(self) -> int:
        return len(self._active_spans)
    def completed_count(self) -> int:
        return len(self._completed)
    def set_attribute(self, span_id: str, key: str, value: Any) -> bool:
        if span_id in self._active_spans:
            self._active_spans[span_id]["attributes"][key] = value
            return True
        return False
