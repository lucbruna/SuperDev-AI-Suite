"""Performance subsystem generator."""
import os

BASE = r'C:\Users\tomga\OneDrive\Desktop\super_dev_suite\SuperDev\ai\observability\performance'

def w(path, content):
    full = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(content)

w('performance_engine.py', '''"""Performance engine."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time

class PerformanceEngine:
    def __init__(self) -> None:
        self._benchmarks: Dict[str, List[float]] = {}
        self._profiles: Dict[str, Dict[str, Any]] = {}
        self._started = False
    def start(self) -> None:
        self._started = True
    def stop(self) -> None:
        self._started = False
    def record_benchmark(self, name: str, duration_ms: float) -> None:
        self._benchmarks.setdefault(name, []).append(duration_ms)
        if len(self._benchmarks[name]) > 1000:
            self._benchmarks[name] = self._benchmarks[name][-1000:]
    def get_benchmark_stats(self, name: str) -> Dict[str, float]:
        values = self._benchmarks.get(name, [])
        if not values:
            return {"min": 0, "max": 0, "avg": 0, "count": 0}
        return {"min": min(values), "max": max(values), "avg": sum(values)/len(values), "count": len(values)}
    def get_status(self) -> Dict[str, Any]:
        return {"running": self._started, "benchmarks": len(self._benchmarks)}
''')

w('benchmark.py', '''"""Performance benchmarks."""
from __future__ import annotations
from typing import Any, Callable, Dict, List
import time

class Benchmark:
    def __init__(self, name: str) -> None:
        self.name = name
        self._results: List[Dict[str, Any]] = []
    def run(self, func: Callable[[], Any], iterations: int = 10) -> Dict[str, Any]:
        durations = []
        for _ in range(iterations):
            start = time.time()
            try:
                func()
                success = True
            except Exception:
                success = False
            durations.append((time.time() - start) * 1000)
        result = {"name": self.name, "iterations": iterations, "min_ms": min(durations), "max_ms": max(durations), "avg_ms": sum(durations)/len(durations), "success_rate": sum(1 for d in durations if d > 0) / iterations}
        self._results.append(result)
        return result
    def get_results(self) -> List[Dict[str, Any]]:
        return list(self._results)
    def get_latest(self) -> Dict[str, Any]:
        return self._results[-1] if self._results else {}

class BenchmarkSuite:
    def __init__(self) -> None:
        self._benchmarks: Dict[str, Benchmark] = {}
    def add_benchmark(self, name: str) -> Benchmark:
        b = Benchmark(name)
        self._benchmarks[name] = b
        return b
    def run_all(self) -> Dict[str, Any]:
        results = {}
        for name, b in self._benchmarks.items():
            results[name] = b.get_latest()
        return results
    def list_benchmarks(self) -> List[str]:
        return list(self._benchmarks.keys())
    def remove_benchmark(self, name: str) -> bool:
        if name in self._benchmarks:
            del self._benchmarks[name]
            return True
        return False
''')

w('profiler.py', '''"""Performance profiler."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class Profiler:
    def __init__(self) -> None:
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._completed: List[Dict[str, Any]] = []
    def start_session(self, name: str) -> str:
        import uuid
        session_id = str(uuid.uuid4())[:8]
        self._sessions[session_id] = {"name": name, "start_time": time.time(), "marks": []}
        return session_id
    def add_mark(self, session_id: str, label: str) -> bool:
        session = self._sessions.get(session_id)
        if session:
            session["marks"].append({"label": label, "time": time.time()})
            return True
        return False
    def end_session(self, session_id: str) -> Dict[str, Any]:
        session = self._sessions.pop(session_id, None)
        if not session:
            return {"error": "session_not_found"}
        session["end_time"] = time.time()
        session["duration_ms"] = (session["end_time"] - session["start_time"]) * 1000
        self._completed.append(session)
        return session
    def get_results(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._completed[-limit:]
    def active_sessions(self) -> int:
        return len(self._sessions)
''')

w('optimization.py', '''"""Performance optimization."""
from __future__ import annotations
from typing import Any, Dict, List

class OptimizationRecommender:
    def __init__(self) -> None:
        self._rules: List[Dict[str, Any]] = []
    def add_rule(self, metric: str, threshold: float, recommendation: str, priority: str = "medium") -> None:
        self._rules.append({"metric": metric, "threshold": threshold, "recommendation": recommendation, "priority": priority})
    def analyze(self, metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        recommendations = []
        for rule in self._rules:
            value = metrics.get(rule["metric"], 0)
            if value > rule["threshold"]:
                recommendations.append({"metric": rule["metric"], "current_value": value, "threshold": rule["threshold"], "recommendation": rule["recommendation"], "priority": rule["priority"]})
        return sorted(recommendations, key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(x["priority"], 4))
    def list_rules(self) -> List[Dict[str, Any]]:
        return list(self._rules)
    def remove_rule(self, index: int) -> bool:
        if 0 <= index < len(self._rules):
            self._rules.pop(index)
            return True
        return False
''')

w('bottleneck.py', '''"""Bottleneck detection."""
from __future__ import annotations
from typing import Any, Dict, List

class BottleneckDetector:
    def __init__(self, threshold_percent: float = 80.0) -> None:
        self._threshold = threshold_percent
        self._measurements: Dict[str, List[float]] = {}
    def record(self, component: str, duration_ms: float) -> None:
        self._measurements.setdefault(component, []).append(duration_ms)
        if len(self._measurements[component]) > 1000:
            self._measurements[component] = self._measurements[component][-1000:]
    def detect(self) -> List[Dict[str, Any]]:
        bottlenecks = []
        all_avgs = {}
        for comp, values in self._measurements.items():
            all_avgs[comp] = sum(values) / len(values) if values else 0
        total = sum(all_avgs.values()) or 1
        for comp, avg in all_avgs.items():
            percent = (avg / total) * 100
            if percent > self._threshold:
                bottlenecks.append({"component": comp, "avg_ms": avg, "percent_of_total": percent})
        return sorted(bottlenecks, key=lambda x: x["percent_of_total"], reverse=True)
    def list_components(self) -> List[str]:
        return list(self._measurements.keys())
    def clear(self) -> int:
        n = sum(len(v) for v in self._measurements.values())
        self._measurements.clear()
        return n
''')

w('recommendation.py', '''"""Performance recommendations."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class PerformanceRecommendation:
    def __init__(self) -> None:
        self._recommendations: List[Dict[str, Any]] = []
    def add(self, category: str, title: str, description: str, priority: str = "medium") -> Dict[str, Any]:
        rec = {"category": category, "title": title, "description": description, "priority": priority, "timestamp": time.time()}
        self._recommendations.append(rec)
        return rec
    def get_by_category(self, category: str) -> List[Dict[str, Any]]:
        return [r for r in self._recommendations if r["category"] == category]
    def get_by_priority(self, priority: str) -> List[Dict[str, Any]]:
        return [r for r in self._recommendations if r["priority"] == priority]
    def get_all(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self._recommendations[-limit:]
    def count(self) -> int:
        return len(self._recommendations)
    def clear(self) -> int:
        n = len(self._recommendations)
        self._recommendations.clear()
        return n
''')

w('__init__.py', '''"""Performance subsystem."""
from .performance_engine import PerformanceEngine
from .benchmark import Benchmark, BenchmarkSuite
from .profiler import Profiler
from .optimization import OptimizationRecommender
from .bottleneck import BottleneckDetector
from .recommendation import PerformanceRecommendation

__all__ = [
    "PerformanceEngine", "Benchmark", "BenchmarkSuite", "Profiler",
    "OptimizationRecommender", "BottleneckDetector", "PerformanceRecommendation"
]
''')

print("performance/: 7 files created")
