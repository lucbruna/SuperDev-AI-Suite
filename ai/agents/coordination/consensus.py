from __future__ import annotations

from typing import Any, Dict, List


class Consensus:
    """Reaches consensus among agents."""

    def __init__(self) -> None:
        self._votes: Dict[str, Dict[str, Any]] = {}

    def vote(self, agent_id: str, topic: str, choice: Any) -> None:
        key = f"{topic}:{agent_id}"
        self._votes[key] = {"agent": agent_id, "topic": topic, "choice": choice}

    def result(self, topic: str) -> Any:
        votes = [v for v in self._votes.values() if v["topic"] == topic]
        if not votes:
            return None
        choices = [v["choice"] for v in votes]
        return max(set(choices), key=choices.count)

    def clear(self) -> None:
        self._votes.clear()

    def to_dict(self) -> Dict[str, Any]:
        return {"votes": list(self._votes.values())}
