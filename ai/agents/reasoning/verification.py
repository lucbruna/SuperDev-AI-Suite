"""Verification engine for validating reasoning conclusions."""

from __future__ import annotations

from typing import Any


class VerificationEngine:
    """Validates reasoning conclusions against facts and evidence."""

    def __init__(self) -> None:
        self._verification_count: int = 0
        self._results: list[dict[str, Any]] = []

    def verify(
        self, conclusion: str, evidence: dict[str, Any], rules: list[dict[str, Any]] | None = None
    ) -> dict[str, Any]:
        self._verification_count += 1
        confidence = 0.5
        issues: list[str] = []
        if evidence:
            confidence += min(len(evidence) * 0.05, 0.25)
        if rules:
            matched = sum(1 for r in rules if any(k in evidence for k in r.get("if", [])))
            confidence += min(matched / max(len(rules), 1) * 0.2, 0.2)
        if len(conclusion) < 10:
            issues.append("Conclusion too short for meaningful verification")
        if not evidence:
            issues.append("No evidence provided to support conclusion")
            confidence -= 0.2
        verified = confidence > 0.5 and len(issues) == 0
        result = {
            "verified": verified,
            "confidence": round(min(max(confidence, 0.0), 1.0), 2),
            "issues": issues,
            "conclusion": conclusion[:200],
            "evidence_count": len(evidence),
        }
        self._results.append(result)
        return result

    def verify_chain(self, steps: list[dict[str, Any]]) -> dict[str, Any]:
        self._verification_count += 1
        chain_valid = True
        step_results: list[dict[str, Any]] = []
        for i, step in enumerate(steps):
            valid = bool(step.get("conclusion")) and bool(step.get("evidence", {}))
            if not valid:
                chain_valid = False
            step_results.append({"step": i, "valid": valid})
        return {"chain_valid": chain_valid, "steps": step_results}

    def get_results(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._results[-limit:]

    def snapshot(self) -> dict[str, Any]:
        verified_count = sum(1 for r in self._results if r.get("verified"))
        return {
            "total_verifications": self._verification_count,
            "verified_count": verified_count,
            "verification_rate": round(verified_count / max(len(self._results), 1), 2),
        }
