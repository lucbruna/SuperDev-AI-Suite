"""Performance benchmarks."""
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
