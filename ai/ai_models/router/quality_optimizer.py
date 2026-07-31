"""Quality optimizer."""
from __future__ import annotations
from typing import Any, Dict, List

class QualityOptimizer:
    def __init__(self) -> None:
        self._scores: Dict[str, Dict[str, float]] = {}
    def record_score(self, model_id: str, task_type: str, score: float) -> None:
        self._scores.setdefault(model_id, {})
        key = task_type
        if key in self._scores[model_id]:
            old = self._scores[model_id][key]
            self._scores[model_id][key] = (old + score) / 2
        else:
            self._scores[model_id][key] = score
    def get_score(self, model_id: str, task_type: str) -> float:
        return self._scores.get(model_id, {}).get(task_type, 0.0)
    def get_average_score(self, model_id: str) -> float:
        scores = self._scores.get(model_id, {})
        if not scores:
            return 0.0
        return sum(scores.values()) / len(scores)
    def best_model_for_task(self, task_type: str) -> str:
        best_model = ""
        best_score = -1
        for model_id, scores in self._scores.items():
            score = scores.get(task_type, 0)
            if score > best_score:
                best_score = score
                best_model = model_id
        return best_model
    def rank_models(self, task_type: str = "") -> List[Dict[str, Any]]:
        rankings = []
        for model_id, scores in self._scores.items():
            if task_type:
                score = scores.get(task_type, 0)
            else:
                score = sum(scores.values()) / len(scores) if scores else 0
            rankings.append({"model_id": model_id, "score": score})
        return sorted(rankings, key=lambda x: x["score"], reverse=True)
    def list_models(self) -> List[str]:
        return list(self._scores.keys())
    def clear(self, model_id: str = "") -> int:
        if model_id:
            n = len(self._scores.get(model_id, {}))
            self._scores.pop(model_id, None)
            return n
        n = sum(len(v) for v in self._scores.values())
        self._scores.clear()
        return n
