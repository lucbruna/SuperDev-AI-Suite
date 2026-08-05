"""SecurityAgent: deterministic rule-based security scanning and risk scoring."""
from __future__ import annotations

from typing import Any

from aios.agents.base_agent import BaseAgent

SEVERITY_ORDER = {"low": 1, "medium": 2, "high": 3, "critical": 4}

DEFAULT_RULES: dict[str, dict[str, str]] = {
    "hardcoded_secret": {"pattern": "password =", "severity": "critical"},
    "sql_injection": {"pattern": "SELECT * FROM", "severity": "high"},
    "eval_usage": {"pattern": "eval(", "severity": "medium"},
    "insecure_http": {"pattern": "http://", "severity": "low"},
}


class SecurityAgent(BaseAgent):
    def __init__(self, name: str = "security", rules: dict[str, dict[str, str]] | None = None, **kwargs: Any) -> None:
        super().__init__(
            name=name,
            role="security",
            capabilities=["security_scan", "risk_assessment", "policy_check"],
            description="Scans for vulnerabilities and scores risk",
            **kwargs,
        )
        self.rules = dict(rules or DEFAULT_RULES)

    def process(self, input_data: Any, context: dict[str, Any]) -> Any:
        text = input_data if isinstance(input_data, str) else str(input_data.get("code", ""))
        findings = []
        for rule, conf in sorted(self.rules.items()):
            if conf["pattern"] in text:
                findings.append({"rule": rule, "severity": conf["severity"]})
        max_sev = max([SEVERITY_ORDER[f["severity"]] for f in findings], default=0)
        if max_sev == 0:
            overall = "clean"
        elif max_sev >= 4:
            overall = "critical"
        elif max_sev == 3:
            overall = "high"
        elif max_sev == 2:
            overall = "medium"
        else:
            overall = "low"
        return {
            "status": overall,
            "findings": findings,
            "risk_score": max_sev,
            "recommendations": [f"fix {f['rule']}" for f in findings] or ["no issues found"],
        }
