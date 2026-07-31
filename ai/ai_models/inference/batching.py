"""Batch processing."""
from __future__ import annotations
from typing import Any, Callable, Dict, List
import time

class BatchProcessor:
    def __init__(self, batch_size: int = 32) -> None:
        self._batch_size = batch_size
        self._batches: Dict[str, List[Dict[str, Any]]] = {}
        self._results: Dict[str, List[Dict[str, Any]]] = {}
    def create_batch(self, batch_id: str, items: List[Dict[str, Any]]) -> str:
        self._batches[batch_id] = items
        self._results[batch_id] = []
        return batch_id
    def process_batch(self, batch_id: str, processor: Callable) -> List[Dict[str, Any]]:
        items = self._batches.get(batch_id, [])
        results = []
        for item in items:
            try:
                result = processor(item)
                results.append({"status": "completed", "result": result})
            except Exception as e:
                results.append({"status": "failed", "error": str(e)})
        self._results[batch_id] = results
        return results
    def get_results(self, batch_id: str) -> List[Dict[str, Any]]:
        return list(self._results.get(batch_id, []))
    def batch_size(self, batch_id: str) -> int:
        return len(self._batches.get(batch_id, []))
    def completed_count(self, batch_id: str) -> int:
        return sum(1 for r in self._results.get(batch_id, []) if r["status"] == "completed")
    def failed_count(self, batch_id: str) -> int:
        return sum(1 for r in self._results.get(batch_id, []) if r["status"] == "failed")
    def list_batches(self) -> List[str]:
        return list(self._batches.keys())
    def delete_batch(self, batch_id: str) -> bool:
        if batch_id in self._batches:
            del self._batches[batch_id]
            self._results.pop(batch_id, None)
            return True
        return False
    def set_batch_size(self, size: int) -> None:
        self._batch_size = size
    def get_batch_size(self) -> int:
        return self._batch_size
