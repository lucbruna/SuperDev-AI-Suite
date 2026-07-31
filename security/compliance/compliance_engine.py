"""Compliance subsystem (Volume 16) — controls evaluation (SOC2/GDPR/HIPAA)."""

from __future__ import annotations

from typing import Any

from ..security_models import ComplianceResult, ComplianceStatus


class ComplianceEngine:
    """Evaluate compliance controls against industry standards."""

    name = "compliance"
    description = "Compliance evaluation: SOC2, GDPR, HIPAA"

    # Standard -> control id -> control name.
    STANDARD_CONTROLS: dict[str, dict[str, str]] = {
        "SOC2": {
            "CC1": "Control environment",
            "CC2": "Communication and information",
            "CC3": "Risk assessment",
            "CC4": "Monitoring activities",
            "CC5": "Control activities",
            "CC6": "Logical and physical access",
            "CC7": "System operations",
            "CC8": "Change management",
            "CC9": "Risk mitigation",
        },
        "GDPR": {
            "ART5": "Lawfulness of processing",
            "ART17": "Right to erasure",
            "ART32": "Security of processing",
            "ART33": "Breach notification",
            "ART35": "Data protection impact assessment",
        },
        "HIPAA": {
            "164.308": "Administrative safeguards",
            "164.310": "Physical safeguards",
            "164.312": "Technical safeguards",
            "164.314": "Organizational requirements",
        },
    }

    def __init__(self, engine: Any | None = None) -> None:
        self.engine = engine
        self._results: dict[str, ComplianceResult] = {}

    def evaluate(
        self,
        standard: str,
        controls_status: dict[str, bool] | None = None,
        target: str = "",
    ) -> ComplianceResult:
        """Evaluate a standard against the provided control statuses.

        ``controls_status`` maps control id -> passed(bool). Missing controls
        default to pending (not yet evaluated).
        """
        standard = standard.upper()
        controls_map = self.STANDARD_CONTROLS.get(standard)
        if controls_map is None:
            return ComplianceResult(
                standard=standard,
                status=ComplianceStatus.NOT_APPLICABLE,
                gaps=["unsupported standard"],
            )

        statuses = controls_status or {}
        controls: list[dict[str, object]] = []
        gaps: list[str] = []
        for control_id, name in controls_map.items():
            passed = statuses.get(control_id)
            if passed is None:
                status = ComplianceStatus.PENDING
            elif passed:
                status = ComplianceStatus.COMPLIANT
            else:
                status = ComplianceStatus.NON_COMPLIANT
                gaps.append(control_id)
            controls.append({"id": control_id, "name": name, "status": status.value})

        evaluated = [c for c in controls if c["status"] != "pending"]
        score = (
            round(
                sum(1 for c in evaluated if c["status"] == "compliant") / len(evaluated),
                4,
            )
            if evaluated
            else 0.0
        )
        status = (
            ComplianceStatus.COMPLIANT
            if not gaps and evaluated
            else ComplianceStatus.NON_COMPLIANT
        )
        result = ComplianceResult(
            standard=standard,
            status=status,
            score=score,
            controls=controls,
            gaps=gaps,
        )
        self._results[f"{standard}:{target}"] = result
        if self.engine is not None:
            self.engine.metrics.increment(
                "security.compliance_evaluations", labels={"standard": standard}
            )
        return result

    def results(self, standard: str | None = None) -> list[ComplianceResult]:
        if standard is None:
            return list(self._results.values())
        return [r for r in self._results.values() if r.standard == standard.upper()]

    def status(self) -> dict[str, Any]:
        return {"evaluations": len(self._results), "standards": sorted(self.STANDARD_CONTROLS)}
