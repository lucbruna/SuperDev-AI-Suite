"""Tracing subsystem engine."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time

class TracingEngine:
    def __init__(self, sample_rate: float = 0.1) -> None:
        self._sample_rate = sample_rate
        self._traces: Dict[str, List[Dict[str, Any]]] = {}
        self._started = False
    def start(self) -> None:
        self._started = True
    def stop(self) -> None:
        self._started = False
    def is_running(self) -> bool:
        return self._started
    def should_sample(self) -> bool:
        import random
        return random.random() < self._sample_rate
    def get_trace(self, trace_id: str) -> List[Dict[str, Any]]:
        return self._traces.get(trace_id, [])
    def get_all_traces(self, limit: int = 50) -> Dict[str, List[Dict[str, Any]]]:
        return dict(list(self._traces.items())[-limit:])
    def get_status(self) -> Dict[str, Any]:
        return {"running": self._started, "traces": len(self._traces), "sample_rate": self._sample_rate}
