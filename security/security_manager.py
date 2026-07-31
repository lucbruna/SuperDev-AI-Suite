"""Manager facade for the Security Engine (Volume 16)."""

from __future__ import annotations

import asyncio
from typing import Any


class SecurityManager:
    """High-level facade coordinating security operations."""

    def __init__(self, engine: Any) -> None:
        self.engine = engine

    async def run_full_security_check(self, target: str, _source: str = "") -> dict[str, Any]:
        """Run all available scans/checks against a target and aggregate."""
        results: dict[str, Any] = {"target": target, "scans": {}}
        for name, subsystem in self.engine.subsystems().items():
            analyzer = getattr(subsystem, "analyze", None)
            if analyzer is None:
                continue
            try:
                report = analyzer(target)
                if asyncio.iscoroutine(report):
                    report = await report
                results["scans"][name] = report.to_dict() if hasattr(report, "to_dict") else report
            except Exception as exc:  # noqa: BLE001 - aggregate failures
                results["scans"][name] = {"error": str(exc)}
        results["total_findings"] = sum(
            s.get("total_findings", 0) for s in results["scans"].values()
        )
        return results

    def policy_summary(self) -> dict[str, Any]:
        return self.engine.registry.summary()

    def security_score(self) -> float:
        """Composite risk-based score: 1.0 when no findings, lower otherwise."""
        summary = self.engine.registry.summary()
        findings = summary.get("findings", 0)
        if findings == 0:
            return 1.0
        return max(0.0, round(1.0 - 0.1 * findings, 4))
