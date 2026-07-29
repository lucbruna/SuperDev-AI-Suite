"""
Decision History - Records and queries decision history
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID


class DecisionHistory:
    """Records decision history"""

    def __init__(self, config):
        self.config = config
        self._decisions: Dict[UUID, Dict] = {}

    async def initialize(self) -> None:
        pass

    async def record(
        self,
        decision_id: UUID,
        context: Dict,
        options: List[Dict],
        selected: Dict,
        rationale: str,
        confidence: float,
        policy_evaluations: List[Dict],
        made_by: Optional[UUID] = None,
    ) -> UUID:
        record = {
            "decision_id": decision_id,
            "context": context,
            "options": options,
            "selected": selected,
            "rationale": rationale,
            "confidence": confidence,
            "policy_evaluations": policy_evaluations,
            "made_by": str(made_by) if made_by else None,
            "recorded_at": datetime.utcnow().isoformat(),
        }
        self._decisions[decision_id] = record
        return decision_id

    async def query(
        self,
        decision_id: Optional[UUID] = None,
        context_filter: Optional[Dict] = None,
        made_by: Optional[UUID] = None,
        limit: int = 50,
    ) -> List[Dict]:
        results = list(self._decisions.values())

        if decision_id:
            results = [d for d in results if d["decision_id"] == decision_id]
        if made_by:
            results = [d for d in results if d["made_by"] == str(made_by)]

        return results[-limit:]

    def get_stats(self) -> Dict:
        return {"decisions_recorded": len(self._decisions)}