from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from backend.audit.audit_logger import AuditLogger
from backend.security.compliance import ComplianceEngine


class ComplianceReporter:
    def __init__(self):
        self._audit = AuditLogger()
        self._compliance = ComplianceEngine()

    def _format_duration(self, days: int) -> str:
        if days < 30:
            return f"{days} days"
        if days < 365:
            return f"{days // 30} months"
        return f"{days // 365} years"

    def generate_soc2_report(self) -> dict[str, Any]:
        result = self._compliance.check_compliance("SOC2")
        return {
            "framework": "SOC2",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "compliant": result.get("compliant", False),
            "passed": result.get("passed", 0),
            "failed": result.get("failed", 0),
            "total": result.get("total", 0),
            "rules": result.get("rules", []),
            "audit_log_count": len(self._audit._entries) if hasattr(self._audit, "_entries") else 0,
        }

    def generate_gdpr_report(self) -> dict[str, Any]:
        result = self._compliance.check_compliance("GDPR")
        return {
            "framework": "GDPR",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "compliant": result.get("compliant", False),
            "rules": result.get("rules", []),
        }

    def generate_hipaa_report(self) -> dict[str, Any]:
        result = self._compliance.check_compliance("HIPAA")
        return {
            "framework": "HIPAA",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "compliant": result.get("compliant", False),
            "rules": result.get("rules", []),
        }

    def generate_full_report(self) -> dict[str, Any]:
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "soc2": self.generate_soc2_report(),
            "gdpr": self.generate_gdpr_report(),
            "hipaa": self.generate_hipaa_report(),
        }

    def export_summary_markdown(self) -> str:
        report = self.generate_full_report()
        lines = ["# Compliance Report", f"Generated: {report['generated_at']}", ""]
        for framework in ["soc2", "gdpr", "hipaa"]:
            data = report[framework]
            status = "✅ COMPLIANT" if data.get("compliant") else "❌ NON-COMPLIANT"
            lines.append(f"## {framework.upper()} — {status}")
            for rule in data.get("rules", []):
                passed = rule.get("passed", rule.get("status")) == "passed"
                lines.append(f"- {'✅' if passed else '❌'} {rule.get('name', rule.get('rule', 'Unknown'))}")
            lines.append("")
        return "\n".join(lines)