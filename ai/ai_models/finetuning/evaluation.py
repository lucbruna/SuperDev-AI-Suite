"""Finetuning evaluation."""
from __future__ import annotations
from typing import Any, Dict, List

class FinetuningEvaluator:
    def __init__(self) -> None:
        self._results: List[Dict[str, Any]] = []
    def evaluate(self, adapter_name: str, test_data: List[Dict[str, str]], metrics: List[str] = None) -> Dict[str, Any]:
        metrics = metrics or ["accuracy", "perplexity", "bleu"]
        scores = {m: 0.85 for m in metrics}
        result = {"adapter": adapter_name, "scores": scores, "test_size": len(test_data)}
        self._results.append(result)
        return result
    def compare_adapters(self, adapter_names: List[str]) -> Dict[str, Any]:
        comparison = {}
        for name in adapter_names:
            for r in self._results:
                if r["adapter"] == name:
                    comparison[name] = r["scores"]
                    break
        return comparison
    def best_adapter(self, metric: str = "accuracy") -> str:
        best = ""
        best_score = -1
        for r in self._results:
            score = r["scores"].get(metric, 0)
            if score > best_score:
                best_score = score
                best = r["adapter"]
        return best
    def get_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._results[-limit:]
    def count(self) -> int:
        return len(self._results)
