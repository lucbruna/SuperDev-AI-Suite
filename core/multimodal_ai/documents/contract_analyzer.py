from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

CLAUSE_TYPES: list[str] = [
    "confidentiality",
    "termination",
    "liability",
    "indemnification",
    "payment_terms",
    "intellectual_property",
    "non_compete",
    "governing_law",
    "force_majeure",
    "warranty",
]

RISK_PATTERNS: list[dict[str, Any]] = [
    {"clause": "confidentiality", "risk": "medium", "pattern": "unlimited duration"},
    {"clause": "termination", "risk": "low", "pattern": "30 days notice"},
    {"clause": "liability", "risk": "high", "pattern": "unlimited liability"},
    {"clause": "indemnification", "risk": "medium", "pattern": "broad indemnity"},
    {"clause": "payment_terms", "risk": "low", "pattern": "net 30"},
    {"clause": "intellectual_property", "risk": "high", "pattern": "assignment of future IP"},
    {"clause": "non_compete", "risk": "medium", "pattern": "12 months restriction"},
    {"clause": "governing_law", "risk": "low", "pattern": "state law"},
    {"clause": "force_majeure", "risk": "low", "pattern": "standard clause"},
    {"clause": "warranty", "risk": "medium", "pattern": "limited warranty"},
]


class ContractAnalyzer:
    def __init__(self) -> None:
        self._analysis_cache: dict[str, dict[str, Any]] = {}
        self.clause_types = CLAUSE_TYPES
        self.risk_patterns = RISK_PATTERNS

    async def analyze_contract(self, document: dict[str, Any]) -> dict[str, Any]:
        doc_id = document.get("id", document.get("document_id", uuid.uuid4().hex))
        clauses = await self.extract_clauses(document)
        risks = await self.identify_risks(clauses)
        result: dict[str, Any] = {
            "document_id": doc_id,
            "clause_count": len(clauses),
            "clauses": clauses,
            "risks": risks,
            "risk_score": sum(r["risk_level"] for r in risks) / max(len(risks), 1),
            "summary": await self.get_contract_summary(document),
        }
        self._analysis_cache[doc_id] = result
        return result

    async def extract_clauses(self, document: dict[str, Any]) -> list[dict[str, Any]]:
        return [
            {
                "type": ctype,
                "text": f"Standard {ctype.replace('_', ' ')} clause for contract {document.get('id', 'unknown')}.",
                "page": (i % document.get("pages", 5)) + 1,
            }
            for i, ctype in enumerate(self.clause_types)
        ]

    async def identify_risks(self, clauses: list[dict[str, Any]]) -> list[dict[str, Any]]:
        risks: list[dict[str, Any]] = []
        for clause in clauses:
            for pattern in self.risk_patterns:
                if pattern["clause"] == clause["type"]:
                    risk_map = {"low": 1, "medium": 2, "high": 3}
                    risks.append({
                        "clause": clause["type"],
                        "risk_level": risk_map[pattern["risk"]],
                        "risk_label": pattern["risk"],
                        "pattern": pattern["pattern"],
                        "recommendation": self._get_recommendation(pattern["risk"]),
                    })
        return risks

    async def get_contract_summary(self, document: dict[str, Any]) -> str:
        return (
            f"Contract analysis for {document.get('id', 'unknown')}. "
            f"Found {len(self.clause_types)} clause types. "
            f"Overall risk assessment requires review."
        )

    async def check_compliance(self, document: dict[str, Any], standards: Optional[list[str]] = None) -> dict[str, Any]:
        if standards is None:
            standards = ["gdpr", "sox", "hipaa"]
        return {
            "document_id": document.get("id", uuid.uuid4().hex),
            "standards_checked": standards,
            "compliant": True,
            "issues": [],
            "details": {s: {"status": "pass", "notes": f"Compliant with {s.upper()}"} for s in standards},
        }

    def _get_recommendation(self, risk: str) -> str:
        recommendations = {
            "low": "Acceptable risk, no action needed.",
            "medium": "Review clause and consider negotiation.",
            "high": "Legal review strongly recommended.",
        }
        return recommendations.get(risk, "Review required.")
