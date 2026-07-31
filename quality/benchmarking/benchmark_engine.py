from __future__ import annotations

import statistics
import time
from collections.abc import Callable
from typing import Any


class BenchmarkEngine:
    """Benchmarking — benchmark suite, comparison, historical data, ranking."""

    def __init__(self, engine: Any) -> None:
        self.engine = engine
        self.config = engine.config.benchmarking
        self._suites: dict[str, dict[str, Any]] = {}
        self._history: dict[str, list[dict[str, Any]]] = {}
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True

    async def shutdown(self) -> None:
        self._initialized = False

    # -- suites --------------------------------------------------------------

    def register_suite(self, name: str, operations: dict[str, Callable[[], Any]]) -> dict[str, Any]:
        suite = {"name": name, "operations": operations, "results": {}}
        self._suites[name] = suite
        return suite

    def list_suites(self) -> list[str]:
        return list(self._suites.keys())

    # -- run -----------------------------------------------------------------

    def run(self, suite_name: str, iterations: int = 5) -> dict[str, Any]:
        """Benchmark every operation in a suite and record per-op latency."""
        suite = self._suites.get(suite_name)
        if suite is None:
            raise ValueError(f"Benchmark suite not found: {suite_name}")
        results: dict[str, dict[str, Any]] = {}
        for op_name, operation in suite["operations"].items():
            latencies: list[float] = []
            error: str | None = None
            for _ in range(max(1, iterations)):
                started = time.perf_counter()
                try:
                    operation()
                except Exception as exc:  # noqa: BLE001 - benchmark captures failures
                    error = str(exc)
                    break
                latencies.append((time.perf_counter() - started) * 1000)
            if error is not None:
                results[op_name] = {
                    "error": error,
                    "avg_ms": float("inf"),
                    "runs": len(latencies),
                }
            else:
                results[op_name] = {
                    "avg_ms": round(statistics.mean(latencies), 4),
                    "min_ms": round(min(latencies), 4),
                    "max_ms": round(max(latencies), 4),
                    "runs": len(latencies),
                }
        suite["results"] = results
        self._history.setdefault(suite_name, []).append({
            "ts": time.time(),
            "results": results,
        })
        self.engine.metrics.increment("benchmarking.runs", labels={"suite": suite_name})
        return results

    # -- comparison ----------------------------------------------------------

    def compare(self, suite_name: str, a: str, b: str) -> dict[str, Any]:
        """Compare two operations within a suite's latest results."""
        results = self._suites.get(suite_name, {}).get("results", {})
        ra = results.get(a)
        rb = results.get(b)
        if not ra or not rb:
            return {"available": False}
        return {
            "available": True,
            "a": {"op": a, "avg_ms": ra["avg_ms"]},
            "b": {"op": b, "avg_ms": rb["avg_ms"]},
            "winner": a if ra["avg_ms"] <= rb["avg_ms"] else b,
            "speedup": (
                round(rb["avg_ms"] / ra["avg_ms"], 2)
                if ra["avg_ms"] and rb["avg_ms"]
                else 1.0
            ),
        }

    # -- historical ----------------------------------------------------------

    def history(self, suite_name: str) -> list[dict[str, Any]]:
        return list(self._history.get(suite_name, []))

    def trend(self, suite_name: str, op: str) -> list[float]:
        """Extract the latency trend for one operation over runs."""
        return [
            run["results"].get(op, {}).get("avg_ms", 0.0)
            for run in self._history.get(suite_name, [])
            if op in run["results"]
        ]

    # -- ranking -------------------------------------------------------------

    def rank_operations(self, suite_name: str) -> list[dict[str, Any]]:
        """Rank operations in a suite by average latency (fastest first)."""
        results = self._suites.get(suite_name, {}).get("results", {})
        ranked = sorted(
            ({"op": op, "avg_ms": info["avg_ms"]} for op, info in results.items()),
            key=lambda item: item["avg_ms"],
        )
        return ranked

    def status(self) -> dict[str, Any]:
        return {
            "initialized": self._initialized,
            "suites": len(self._suites),
            "history_runs": sum(len(v) for v in self._history.values()),
        }


__all__ = ["BenchmarkEngine"]
