"""Evaluation engine."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class EvaluationEngine:
    def __init__(self) -> None:
        self._results: Dict[str, List[Dict[str, Any]]] = {}
        self._benchmarks: Dict[str, Dict[str, Any]] = {}
        self._started = False
    def start(self) -> None:
        self._started = True
    def evaluate(self, model_id: str, test_cases: List[Dict[str, Any]], evaluator: str = "default") -> Dict[str, Any]:
        scores = []
        for tc in test_cases:
            score = tc.get("expected_score", 0.8)
            scores.append({"input": tc.get("input", "")[:50], "score": score})
        avg_score = sum(s["score"] for s in scores) / len(scores) if scores else 0
        result = {"model_id": model_id, "evaluator": evaluator, "test_count": len(test_cases), "avg_score": avg_score, "scores": scores, "timestamp": time.time()}
        self._results.setdefault(model_id, []).append(result)
        return result
    def get_results(self, model_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        return self._results.get(model_id, [])[-limit:]
    def compare(self, model_ids: List[str]) -> Dict[str, Any]:
        comparison = {}
        for mid in model_ids:
            results = self._results.get(mid, [])
            if results:
                latest = results[-1]
                comparison[mid] = {"avg_score": latest["avg_score"], "test_count": latest["test_count"]}
        return comparison
    def best_model(self) -> str:
        best = ""
        best_score = -1
        for mid, results in self._results.items():
            if results:
                score = results[-1]["avg_score"]
                if score > best_score:
                    best_score = score
                    best = mid
        return best
    def list_models(self) -> List[str]:
        return list(self._results.keys())
    def is_running(self) -> bool:
        return self._started
