from __future__ import annotations

from typing import Any


class ChainOptimizer:
    """Optimizes reasoning chains for efficiency."""

    def __init__(self) -> None:
        self._rules: list[dict[str, Any]] = []

    def add_rule(self, rule: dict[str, Any]) -> None:
        self._rules.append(rule)

    async def optimize(self, chain: dict[str, Any]) -> dict[str, Any]:
        steps = list(chain.get("steps", []))
        for rule in self._rules:
            action = rule.get("action", "")
            if action == "merge_adjacent":
                merged = []
                i = 0
                while i < len(steps):
                    if i + 1 < len(steps) and steps[i].get("type") == steps[i + 1].get("type"):
                        merged.append(
                            {**steps[i], "description": f"{steps[i]['description']}; {steps[i + 1]['description']}"}
                        )
                        i += 2
                    else:
                        merged.append(steps[i])
                        i += 1
                steps = merged
            if action == "remove_unnecessary":
                steps = [s for s in steps if s.get("type") != "noop"]
        return {**chain, "steps": steps, "optimized": True}

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        chain = context.get("chain", {})
        return await self.optimize(chain)
