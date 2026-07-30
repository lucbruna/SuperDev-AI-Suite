from __future__ import annotations

from typing import Any, Dict, List


class IncrementalLearning:
    """Supports incremental/online learning without full retraining."""

    def __init__(self):
        self._data: List[Dict[str, Any]] = []
        self._update_count: int = 0

    @property
    def data(self) -> List[Dict[str, Any]]:
        return list(self._data)

    @property
    def update_count(self) -> int:
        return self._update_count

    def update(self, new_data: List[Dict[str, Any]]) -> int:
        self._data.extend(new_data)
        self._update_count += 1
        return len(new_data)

    def update_single(self, item: Dict[str, Any]) -> None:
        self._data.append(item)
        self._update_count += 1

    def summary(self) -> Dict[str, Any]:
        return {
            "total_samples": len(self._data),
            "update_count": self._update_count,
            "types": list({d.get("type", "unknown") for d in self._data}),
        }

    def clear(self) -> None:
        self._data.clear()
        self._update_count = 0
