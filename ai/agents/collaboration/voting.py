from __future__ import annotations

from typing import Any, Dict, List


class Voting:
    """Voting mechanism for group decisions."""

    def __init__(self) -> None:
        self._ballots: Dict[str, Dict[str, Any]] = {}

    def cast(self, voter: str, topic: str, choice: Any) -> None:
        key = f"{topic}:{voter}"
        self._ballots[key] = {"voter": voter, "topic": topic, "choice": choice}

    def tally(self, topic: str) -> Dict[Any, int]:
        votes = [v for v in self._ballots.values() if v["topic"] == topic]
        counts: Dict[Any, int] = {}
        for v in votes:
            counts[v["choice"]] = counts.get(v["choice"], 0) + 1
        return counts

    def winner(self, topic: str) -> Any:
        counts = self.tally(topic)
        if not counts:
            return None
        return max(counts, key=counts.get)

    def clear(self) -> None:
        self._ballots.clear()
