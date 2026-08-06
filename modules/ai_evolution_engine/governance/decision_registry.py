"""Decision registry: records governance decisions for traceability."""
from __future__ import annotations

from dataclasses import dataclass, field

from modules.ai_evolution_engine.config.constants import DECISION_PENDING
from modules.ai_evolution_engine.core.evolution_context import EvolutionContext


@dataclass(slots=True)
class DecisionRecord:
    """A recorded governance decision."""

    subject: str
    decision: str = DECISION_PENDING
    reason: str = ""
    sequence: int = 0

    def to_dict(self) -> dict[str, object]:
        return {
            "subject": self.subject,
            "decision": self.decision,
            "reason": self.reason,
            "sequence": self.sequence,
        }


class DecisionRegistry:
    """Stores decisions in context memory for later reconciliation."""

    def __init__(self, key: str = "governance_decisions") -> None:
        self._key = key

    def record(
        self, ctx: EvolutionContext, subject: str, decision: str, reason: str = ""
    ) -> None:
        records = list(ctx.memory.recall(self._key, []) or [])
        records.append(
            DecisionRecord(
                subject=subject,
                decision=decision,
                reason=reason,
                sequence=len(records) + 1,
            ).to_dict()
        )
        ctx.memory.remember(self._key, records)

    def decisions(self, ctx: EvolutionContext) -> list[DecisionRecord]:
        records = ctx.memory.recall(self._key, []) or []
        return [
            DecisionRecord(
                subject=r["subject"],
                decision=r["decision"],
                reason=r.get("reason", ""),
                sequence=int(r.get("sequence", 0)),
            )
            for r in records
            if isinstance(r, dict)
        ]
