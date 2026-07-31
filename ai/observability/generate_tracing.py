"""Tracing subsystem generator."""
import os
BASE = r'C:\Users\tomga\OneDrive\Desktop\super_dev_suite\SuperDev\ai\observability\tracing'

def w(path, content):
    full = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(content)

w('tracing_engine.py', '''"""Tracing subsystem engine."""
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
''')

w('trace_collector.py', '''"""Trace collector."""
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
''')

w('span_manager.py', '''"""Span management."""
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
''')

w('transaction.py', '''"""Transaction management."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time, uuid

class TransactionManager:
    def __init__(self) -> None:
        self._transactions: Dict[str, Dict[str, Any]] = {}
    def start_transaction(self, name: str, transaction_type: str = "request") -> str:
        tx_id = str(uuid.uuid4())[:8]
        self._transactions[tx_id] = {"id": tx_id, "name": name, "type": transaction_type, "start_time": time.time(), "spans": [], "status": "active"}
        return tx_id
    def end_transaction(self, tx_id: str, status: str = "success") -> Optional[Dict[str, Any]]:
        tx = self._transactions.get(tx_id)
        if not tx:
            return None
        tx["end_time"] = time.time()
        tx["duration_ms"] = (tx["end_time"] - tx["start_time"]) * 1000
        tx["status"] = status
        return tx
    def add_span_to_transaction(self, tx_id: str, span_id: str) -> bool:
        tx = self._transactions.get(tx_id)
        if tx:
            tx["spans"].append(span_id)
            return True
        return False
    def get_transaction(self, tx_id: str) -> Optional[Dict[str, Any]]:
        return self._transactions.get(tx_id)
    def list_transactions(self) -> List[Dict[str, Any]]:
        return list(self._transactions.values())
    def get_slow_transactions(self, threshold_ms: float = 1000) -> List[Dict[str, Any]]:
        return [t for t in self._transactions.values() if t.get("duration_ms", 0) > threshold_ms]
''')

w('dependency_map.py', '''"""Dependency mapping."""
from __future__ import annotations
from typing import Any, Dict, List, Set

class DependencyMap:
    def __init__(self) -> None:
        self._deps: Dict[str, Set[str]] = {}
        self._reverse: Dict[str, Set[str]] = {}
    def add_dependency(self, source: str, target: str) -> None:
        self._deps.setdefault(source, set()).add(target)
        self._reverse.setdefault(target, set()).add(source)
    def remove_dependency(self, source: str, target: str) -> bool:
        if source in self._deps and target in self._deps[source]:
            self._deps[source].discard(target)
            self._reverse.get(target, set()).discard(source)
            return True
        return False
    def get_dependencies(self, service: str) -> List[str]:
        return list(self._deps.get(service, set()))
    def get_dependents(self, service: str) -> List[str]:
        return list(self._reverse.get(service, set()))
    def get_all_services(self) -> List[str]:
        all_svc = set(self._deps.keys()) | set(self._reverse.keys())
        return sorted(all_svc)
    def has_cycle(self) -> bool:
        visited: Set[str] = set()
        path: Set[str] = set()
        def dfs(node: str) -> bool:
            visited.add(node)
            path.add(node)
            for neighbor in self._deps.get(node, set()):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in path:
                    return True
            path.discard(node)
            return False
        return any(dfs(n) for n in self._deps if n not in visited)
    def to_dict(self) -> Dict[str, List[str]]:
        return {k: list(v) for k, v in self._deps.items()}
''')

w('latency_analysis.py', '''"""Latency analysis."""
from __future__ import annotations
from typing import Any, Dict, List
import statistics

class LatencyAnalyzer:
    def __init__(self) -> None:
        self._latencies: Dict[str, List[float]] = {}
    def record(self, operation: str, latency_ms: float) -> None:
        self._latencies.setdefault(operation, []).append(latency_ms)
        if len(self._latencies[operation]) > 1000:
            self._latencies[operation] = self._latencies[operation][-1000:]
    def analyze(self, operation: str) -> Dict[str, float]:
        values = self._latencies.get(operation, [])
        if not values:
            return {"min": 0, "max": 0, "avg": 0, "p50": 0, "p95": 0, "p99": 0, "count": 0}
        sorted_vals = sorted(values)
        return {
            "min": min(values), "max": max(values), "avg": statistics.mean(values),
            "p50": sorted_vals[len(sorted_vals)//2],
            "p95": sorted_vals[int(len(sorted_vals)*0.95)],
            "p99": sorted_vals[int(len(sorted_vals)*0.99)],
            "count": len(values)
        }
    def get_slow_operations(self, threshold_ms: float = 1000) -> List[Dict[str, Any]]:
        results = []
        for op, values in self._latencies.items():
            avg = sum(values) / len(values) if values else 0
            if avg > threshold_ms:
                results.append({"operation": op, "avg_ms": avg, "count": len(values)})
        return sorted(results, key=lambda x: x["avg_ms"], reverse=True)
    def list_operations(self) -> List[str]:
        return list(self._latencies.keys())
    def clear(self, operation: str = "") -> int:
        if operation:
            n = len(self._latencies.get(operation, []))
            self._latencies.pop(operation, None)
            return n
        n = sum(len(v) for v in self._latencies.values())
        self._latencies.clear()
        return n
''')

w('__init__.py', '''"""Tracing subsystem."""
from .tracing_engine import TracingEngine
from .trace_collector import TraceCollector
from .span_manager import SpanManager
from .transaction import TransactionManager
from .dependency_map import DependencyMap
from .latency_analysis import LatencyAnalyzer

__all__ = [
    "TracingEngine", "TraceCollector", "SpanManager",
    "TransactionManager", "DependencyMap", "LatencyAnalyzer"
]
''')

print("tracing/: 7 files created")
