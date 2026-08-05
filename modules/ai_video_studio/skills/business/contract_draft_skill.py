"""Contract draft skill — contract structure and key clauses."""
from __future__ import annotations
from typing import Any


class ContractDraftSkill:
    """Outline a contract with key clauses and negotiation flags."""

    skill_id = "contract_draft"
    skill_name = "Contract Draft"
    skill_version = "1.0.0"
    skill_description = "Contract outline with standard clauses and risk flags."
    skill_category = "business"
    skill_tags = ["business", "contract", "legal", "clauses"]
    skill_permissions = ["content:plan"]

    def __init__(self) -> None:
        pass

    async def __call__(
        self,
        parties: tuple[str, str],
        *,
        subject: str = "services",
        language: str = "en",
    ) -> dict[str, Any]:
        """Return a contract skeleton listing the standard clauses."""
        party_a, party_b = parties
        return {
            "parties": {"party_a": party_a, "party_b": party_b},
            "subject": subject,
            "language": language,
            "clauses": [
                {"clause": "Recitals", "content": f"Purpose of the agreement between {party_a} and {party_b}."},
                {"clause": "Definitions", "content": "Key terms used in the contract."},
                {"clause": "Scope", "content": f"Deliverables of the {subject} engagement."},
                {"clause": "Fees & Payment", "content": "Compensation, invoicing, and late terms."},
                {"clause": "Term & Termination", "content": "Duration and exit conditions."},
                {"clause": "Confidentiality", "content": "Protection of each party's information."},
                {"clause": "Liability", "content": "Limits and exclusions of liability."},
                {"clause": "Governing Law", "content": "Jurisdiction for disputes."},
            ],
            "risk_flags": ["one-sided termination", "unlimited liability", "missing IP assignment"],
            "note": "Template only — have a qualified lawyer review before signing.",
        }
