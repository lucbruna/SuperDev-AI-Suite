"""Benchmark system."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class BenchmarkRunner:
    def __init__(self) -> None:
        self._benchmarks: Dict[str, Dict[str, Any]] = {}
        self._results: List[Dict[str, Any]] = []
    def register_benchmark(self, name: str, test_cases: List[Dict[str, Any]], category: str = "general") -> Dict[str, Any]:
        bench = {"name": name, "test_cases": test_cases, "category": category, "created_at": time.time()}
        self._benchmarks[name] = bench
        return bench
    def run(self, benchmark_name: str, model_id: str, handler) -> Dict[str, Any]:
        bench = self._benchmarks.get(benchmark_name)
        if not bench:
            return {"error": "benchmark_not_found"}
        results = []
        for tc in bench["test_cases"]:
            try:
                output = handler(tc.get("input", ""))
                score = 1.0 if output else 0.0
                results.append({"input": tc.get("input", "")[:50], "score": score})
            except Exception as e:
                results.append({"input": tc.get("input", "")[:50], "score": 0, "error": str(e)})
        avg = sum(r["score"] for r in results) / len(results) if results else 0
        result = {"benchmark": benchmark_name, "model_id": model_id, "avg_score": avg, "results": results, "timestamp": time.time()}
        self._results.append(result)
        return result
    def get_results(self, benchmark: str = "", model_id: str = "", limit: int = 20) -> List[Dict[str, Any]]:
        results = self._results
        if benchmark:
            results = [r for r in results if r["benchmark"] == benchmark]
        if model_id:
            results = [r for r in results if r["model_id"] == model_id]
        return results[-limit:]
    def list_benchmarks(self) -> List[str]:
        return list(self._benchmarks.keys())
    def remove_benchmark(self, name: str) -> bool:
        if name in self._benchmarks:
            del self._benchmarks[name]
            return True
        return False
    def count(self) -> int:
        return len(self._results)
