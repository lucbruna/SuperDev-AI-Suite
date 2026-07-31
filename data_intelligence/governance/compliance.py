"""Compliance checks (LGPD-style)."""

from __future__ import annotations

from typing import Any

from data_intelligence.data_security import DataIntelligenceSecurity


class ComplianceChecker:
    """Checks datasets against data-protection requirements."""

    def __init__(self, security: DataIntelligenceSecurity) -> None:
        self.security = security

    def check(self, dataset: str, records: list[dict[str, Any]],
              required_fields: tuple[str, ...] = (),
              pii_fields: tuple[str, ...] = ()) -> dict[str, Any]:
        findings: list[dict[str, Any]] = []
        if not records:
            findings.append({"severity": "medium",
                             "finding": "dataset vazio",
                             "dataset": dataset})
        for field in required_fields:
            missing = [record for record in records
                       if field not in record or record[field] in (None, "")]
            if missing:
                findings.append({
                    "severity": "high",
                    "finding": f"campo obrigatório ausente: {field}",
                    "dataset": dataset, "affected": len(missing)})
        for field in pii_fields:
            unprotected = []
            for record in records:
                value = record.get(field)
                if value is not None and "***" not in str(value):
                    unprotected.append(value)
            if unprotected:
                findings.append({
                    "severity": "high",
                    "finding": f"PII não mascarada no campo: {field}",
                    "dataset": dataset, "affected": len(unprotected)})
        high = sum(1 for f in findings if f["severity"] == "high")
        return {"dataset": dataset, "findings": findings,
                "high": high,
                "status": "compliant" if not findings else
                          "non_compliant" if high else "review"}
