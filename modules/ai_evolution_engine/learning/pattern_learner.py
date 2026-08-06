"""Pattern learner: extracts recurring codebase patterns."""
from __future__ import annotations

from dataclasses import dataclass

from modules.ai_evolution_engine.core.evolution_context import EvolutionContext


@dataclass(slots=True)
class CodePattern:
    """A recurring structural or behavioural pattern."""

    name: str
    evidence_count: int
    sample_locations: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "evidence_count": self.evidence_count,
            "sample_locations": list(self.sample_locations),
        }


def learn(ctx: EvolutionContext) -> list[CodePattern]:
    """Extract patterns from context artifacts (deterministic)."""
    patterns: list[CodePattern] = []
    duplicated = list(ctx.get_artifact("duplicated_code", []) or [])
    for location, count in duplicated[:10]:
        patterns.append(
            CodePattern(
                name="duplicated_block",
                evidence_count=int(count),
                sample_locations=(location,),
            )
        )
    hotspots = list(ctx.get_artifact("change_hotspots", []) or [])
    for location, count in hotspots[:10]:
        patterns.append(
            CodePattern(
                name="change_hotspot",
                evidence_count=int(count),
                sample_locations=(location,),
            )
        )
    return patterns
