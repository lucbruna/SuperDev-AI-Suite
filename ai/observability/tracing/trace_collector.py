"""Trace collector."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time, uuid

class TraceCollector:
    def __init__(self, max_traces: int = 1000) -> None:
        self._traces: Dict[str, List[Dict[str, Any]]] = {}
        self._max = max_traces
        self._total_collected = 0
    def collect(self, trace_id: str, span: Dict[str, Any]) -> bool:
        span.setdefault("span_id", str(uuid.uuid4())[:8])
        span.setdefault("timestamp", time.time())
        self._traces.setdefault(trace_id, []).append(span)
        self._total_collected += 1
        if len(self._traces) > self._max:
            oldest = list(self._traces.keys())[0]
            del self._traces[oldest]
        return True
    def get_trace(self, trace_id: str) -> List[Dict[str, Any]]:
        return self._traces.get(trace_id, [])
    def list_traces(self) -> List[str]:
        return list(self._traces.keys())
    def total_collected(self) -> int:
        return self._total_collected
    def trace_count(self) -> int:
        return len(self._traces)
