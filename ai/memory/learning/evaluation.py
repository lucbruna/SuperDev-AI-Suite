from __future__ import annotations

from typing import Any, Dict, List


class Evaluation:
    """Evaluates learning performance and accuracy."""

    def __init__(self):
        self._eval_count: int = 0
        self._last_accuracy: float = 0.0
        self._history: List[Dict[str, Any]] = []

    @property
    def eval_count(self) -> int:
        return self._eval_count

    @property
    def last_accuracy(self) -> float:
        return self._last_accuracy

    @property
    def history(self) -> List[Dict[str, Any]]:
        return list(self._history)

    def evaluate(self, predictions: List[Any], targets: List[Any]) -> float:
        if not predictions or not targets:
            return 0.0
        correct = sum(1 for p, t in zip(predictions, targets) if p == t)
        accuracy = correct / max(len(targets), 1)
        self._last_accuracy = accuracy
        self._eval_count += 1
        self._history.append({"accuracy": accuracy, "samples": len(targets)})
        return accuracy

    def precision_recall(self, predictions: List[Any], targets: List[Any], positive: Any = True) -> Dict[str, float]:
        tp = sum(1 for p, t in zip(predictions, targets) if p == positive and t == positive)
        fp = sum(1 for p, t in zip(predictions, targets) if p == positive and t != positive)
        fn = sum(1 for p, t in zip(predictions, targets) if p != positive and t == positive)
        precision = tp / max(tp + fp, 1)
        recall = tp / max(tp + fn, 1)
        f1 = 2 * precision * recall / max(precision + recall, 1e-9)
        self._eval_count += 1
        return {"precision": precision, "recall": recall, "f1": f1}

    def clear(self) -> None:
        self._eval_count = 0
        self._last_accuracy = 0.0
        self._history.clear()
