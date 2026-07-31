"""Inference engine for drawing conclusions from evidence."""

from __future__ import annotations

from typing import Any


class InferenceEngine:
    """Draws inferences from facts and problem descriptions."""

    def __init__(self) -> None:
        self._inference_count: int = 0

    def infer(self, problem: str, facts: dict[str, Any]) -> list[dict[str, Any]]:
        self._inference_count += 1
        inferences: list[dict[str, Any]] = []
        for key, value in facts.items():
            inferences.append(
                {
                    "type": "from_fact",
                    "premise": f"{key} = {value}",
                    "conclusion": f"Given {key} is {value}, we can proceed",
                    "confidence": 0.8,
                }
            )
        problem_words = problem.lower().split()
        if any(w in problem_words for w in ["optimize", "improve", "better"]):
            inferences.append(
                {
                    "type": "goal_inference",
                    "premise": "Goal involves optimization",
                    "conclusion": "Should measure current state before optimizing",
                    "confidence": 0.7,
                }
            )
        if any(w in problem_words for w in ["fix", "bug", "error", "broken"]):
            inferences.append(
                {
                    "type": "problem_inference",
                    "premise": "Problem involves fixing something",
                    "conclusion": "Should diagnose root cause first",
                    "confidence": 0.75,
                }
            )
        return inferences

    def chain(self, initial_facts: dict[str, Any], rules: list[dict[str, Any]]) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        current = dict(initial_facts)
        for rule in rules:
            condition = rule.get("condition", "")
            if all(k in current for k in condition.split(",") if k.strip()):
                conclusion = rule.get("conclusion", "")
                current[rule.get("output_key", "result")] = conclusion
                results.append(
                    {
                        "rule": rule.get("name", "unnamed"),
                        "conclusion": conclusion,
                    }
                )
        return results

    def snapshot(self) -> dict[str, Any]:
        return {"total_inferences": self._inference_count}
