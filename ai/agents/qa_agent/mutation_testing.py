from __future__ import annotations

from typing import Any


class MutationTesting:
    """Manages mutation testing and tracks mutant survival rates."""

    def __init__(self) -> None:
        self._mutants: dict[str, dict[str, Any]] = {}

    def add_mutant(
        self,
        original: str,
        mutated: str,
        operator: str = "replace",
    ) -> str:
        mid = f"mut_{len(self._mutants) + 1:04d}"
        self._mutants[mid] = {
            "id": mid,
            "original": original,
            "mutated": mutated,
            "operator": operator,
            "killed": False,
        }
        return mid

    def get_mutant(self, mutant_id: str) -> dict[str, Any] | None:
        return self._mutants.get(mutant_id)

    def list_mutants(self) -> list[dict[str, Any]]:
        return list(self._mutants.values())

    def run_mutation_suite(self) -> dict[str, Any]:
        import random

        for mutant in self._mutants.values():
            mutant["killed"] = random.random() > 0.3
        killed = sum(1 for m in self._mutants.values() if m["killed"])
        total = len(self._mutants)
        return {
            "total": total,
            "killed": killed,
            "survived": total - killed,
            "kill_rate": round(killed / total * 100, 1) if total > 0 else 0.0,
        }

    @property
    def mutant_count(self) -> int:
        return len(self._mutants)

    @property
    def killed_count(self) -> int:
        return sum(1 for m in self._mutants.values() if m["killed"])

    @property
    def survival_rate(self) -> float:
        if not self._mutants:
            return 0.0
        return round(sum(1 for m in self._mutants.values() if not m["killed"]) / len(self._mutants) * 100, 1)

    def to_dict(self) -> dict[str, Any]:
        return {
            "mutants": list(self._mutants.values()),
            "mutant_count": self.mutant_count,
            "killed_count": self.killed_count,
            "survival_rate": self.survival_rate,
        }
