from __future__ import annotations

from typing import Any, Dict, List


class Reinforcement:
    """Reinforcement of successful memory patterns."""

    def __init__(self):
        self._reinforcement_log: List[Dict[str, Any]] = []
        self._cycle_count: int = 0

    @property
    def reinforcement_log(self) -> List[Dict[str, Any]]:
        return list(self._reinforcement_log)

    @property
    def cycle_count(self) -> int:
        return self._cycle_count

    def reinforce(self, pattern_id: str, weight: float = 1.0) -> Dict[str, Any]:
        entry: Dict[str, Any] = {
            "pattern_id": pattern_id,
            "reinforcement": weight,
            "cycle": self._cycle_count + 1,
        }
        self._reinforcement_log.append(entry)
        self._cycle_count += 1
        return entry

    def reinforce_batch(self, pattern_ids: List[str], weight: float = 1.0) -> List[Dict[str, Any]]:
        return [self.reinforce(pid, weight) for pid in pattern_ids]

    def get_reinforced_patterns(self, threshold: float = 1.0) -> List[str]:
        accum: Dict[str, float] = {}
        for entry in self._reinforcement_log:
            pid = entry["pattern_id"]
            accum[pid] = accum.get(pid, 0.0) + entry["reinforcement"]
        return [pid for pid, total in accum.items() if total >= threshold]

    def total_reinforcement(self, pattern_id: str) -> float:
        return sum(
            e["reinforcement"]
            for e in self._reinforcement_log
            if e["pattern_id"] == pattern_id
        )

    def clear(self) -> None:
        self._reinforcement_log.clear()
        self._cycle_count = 0
