"""Decomposer: splits a high-level goal into deterministic task specifications."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

DECOMPOSITION_STRATEGIES = ("sequential", "parallel", "hierarchical", "greedy")


@dataclass
class TaskSpec:
    """Specification for a single task produced by a decomposition strategy."""

    name: str
    kind: str = "action"
    description: str = ""
    depends_on: list[str] = field(default_factory=list)
    agent: str | None = None
    params: dict[str, Any] = field(default_factory=dict)
    estimated_duration: float = 1.0
    priority: int = 5
    strategy: str = "hierarchical"


class Decomposer:
    """Deterministic goal decomposition without external model calls.

    Subgoals may be supplied explicitly via ``subgoals=``; otherwise the
    decomposer derives a stable set of subgoals from the goal text by
    splitting on sentence boundaries.
    """

    _ALIASES = {
        "seq": "sequential",
        "sequence": "sequential",
        "linear": "sequential",
        "par": "parallel",
        "independent": "parallel",
        "hier": "hierarchical",
        "tree": "hierarchical",
        "flat": "greedy",
        "simple": "greedy",
    }

    def __init__(self) -> None:
        self._seq = 0

    def _normalize(self, strategy: str) -> str:
        key = (strategy or "hierarchical").strip().lower()
        key = self._ALIASES.get(key, key)
        if key not in DECOMPOSITION_STRATEGIES:
            raise ValueError(
                f"unknown decomposition strategy {strategy!r}; expected one of {DECOMPOSITION_STRATEGIES}"
            )
        return key

    @staticmethod
    def _derive_subgoals(goal: str) -> list[str]:
        """Split the goal text into stable subgoal sentences."""
        text = str(goal).strip()
        parts = [p.strip() for p in re.split(r"[.;!?\n]+", text) if p.strip()]
        return parts or [text]

    def decompose(
        self,
        goal: str,
        strategy: str = "hierarchical",
        subgoals: list[str] | None = None,
        duration: float = 1.0,
    ) -> list[TaskSpec]:
        if not goal or not str(goal).strip():
            raise ValueError("goal must be a non-empty string")
        strategy = self._normalize(strategy)
        derived = [str(s).strip() for s in (subgoals or self._derive_subgoals(goal)) if str(s).strip()]
        if not derived:
            derived = [str(goal).strip()]

        self._seq = 0
        duration = max(0.0, float(duration))
        single = len(derived) == 1

        def name_for(idx: int) -> str:
            return str(goal) if single else f"{goal} #{idx}"

        specs: list[TaskSpec] = []
        for idx in range(1, len(derived) + 1):
            deps: list[str] = []
            if strategy == "sequential" and idx > 1:
                deps = [name_for(idx - 1)]
            kind = "sequential" if strategy == "sequential" else ("subgoal" if strategy == "hierarchical" else "action")
            specs.append(
                TaskSpec(
                    name=name_for(idx),
                    kind=kind,
                    description=derived[idx - 1],
                    depends_on=deps,
                    estimated_duration=duration,
                    strategy=strategy,
                )
            )

        if strategy == "hierarchical" and not single:
            specs.append(
                TaskSpec(
                    name=f"{goal} - merge",
                    kind="action",
                    description=f"consolidate results of {goal}",
                    depends_on=[name_for(i) for i in range(1, len(derived) + 1)],
                    estimated_duration=duration / 2.0,
                    priority=6,
                    strategy=strategy,
                )
            )
        return specs
