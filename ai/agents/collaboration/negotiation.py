from __future__ import annotations

from typing import Any


class Negotiation:
    """Negotiation between agents."""

    def __init__(self) -> None:
        self._proposals: dict[str, dict[str, Any]] = {}
        self._negotiation_count: int = 0

    @property
    def negotiation_count(self) -> int:
        return self._negotiation_count

    def propose(self, proposal_id: str, agent_id: str, terms: dict[str, Any]) -> None:
        self._proposals[proposal_id] = {"agent": agent_id, "terms": terms, "status": "proposed"}
        self._negotiation_count += 1

    def accept(self, proposal_id: str) -> bool:
        prop = self._proposals.get(proposal_id)
        if prop and prop["status"] == "proposed":
            prop["status"] = "accepted"
            return True
        return False

    def reject(self, proposal_id: str) -> bool:
        prop = self._proposals.get(proposal_id)
        if prop and prop["status"] == "proposed":
            prop["status"] = "rejected"
            return True
        return False

    def get_proposal(self, proposal_id: str) -> dict[str, Any] | None:
        prop = self._proposals.get(proposal_id)
        return dict(prop) if prop else None

    def clear(self) -> None:
        self._proposals.clear()
        self._negotiation_count = 0
