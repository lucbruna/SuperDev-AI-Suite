"""Decision engine for selecting best course of action."""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


class DecisionEngine:
    """Selects best course of action from evaluated alternatives."""

    def __init__(self) -> None:
        self._decision_count: int = 0
        self._history: List[Dict[str, Any]] = []

    def decide(self, options: Dict[str, Any]) -> Dict[str, Any]:
        self._decision_count += 1
        hypotheses = options.get("hypotheses", [])
        best = options.get("best")
        decision = {
            "chosen": best["hypothesis"] if best else "default_action",
            "confidence": best["score"] if best else 0.5,
            "alternatives_count": len(hypotheses),
            "reasoning": options.get("problem", ""),
            "timestamp": time.time(),
        }
        self._history.append(decision)
        return decision

    def decide_from_list(self, choices: List[Dict[str, Any]],
                         criteria: Optional[List[str]] = None) -> Dict[str, Any]:
        self._decision_count += 1
        if not choices:
            return {"chosen": None, "error": "No choices provided"}
        scored = []
        for choice in choices:
            score = sum(choice.get(c, 0.5) for c in (criteria or ["score"]))
            score /= max(len(criteria or ["score"]), 1)
            scored.append({"choice": choice, "score": score})
        scored.sort(key=lambda x: x["score"], reverse=True)
        best = scored[0]
        decision = {
            "chosen": best["choice"],
            "score": best["score"],
            "alternatives_count": len(choices),
            "timestamp": time.time(),
        }
        self._history.append(decision)
        return decision

    def get_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._history[-limit:]

    def snapshot(self) -> Dict[str, Any]:
        return {"total_decisions": self._decision_count}
