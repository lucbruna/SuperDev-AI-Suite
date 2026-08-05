"""Policy writer skill — security policy document plan."""
from __future__ import annotations
from typing import Any


class PolicyWriterSkill:
    """Draft a security policy: scope, rules, responsibilities, enforcement."""

    skill_id = "policy_writer"
    skill_name = "Policy Writer"
    skill_version = "1.0.0"
    skill_description = "Security policy document: scope, rules, responsibilities."
    skill_category = "security"
    skill_tags = ["security", "policy", "compliance", "governance"]
    skill_permissions = ["content:plan"]

    def __init__(self) -> None:
        pass

    async def __call__(
        self,
        policy_subject: str,
        *,
        organization: str = "the organization",
        language: str = "en",
    ) -> dict[str, Any]:
        """Return a security policy outline."""
        return {
            "subject": policy_subject,
            "organization": organization,
            "language": language,
            "sections": [
                {"section": "Purpose", "content": f"Why {organization} needs this {policy_subject} policy."},
                {"section": "Scope", "content": "Who and what the policy applies to."},
                {"section": "Rules", "content": f"Concrete requirements for {policy_subject}."},
                {"section": "Responsibilities", "content": "Owner, users, and enforcement roles."},
                {"section": "Enforcement", "content": "Monitoring, violations, and consequences."},
                {"section": "Review", "content": "Cadence for reviewing and updating the policy."},
            ],
            "style": "short declarative sentences, avoid jargon, cite exceptions explicitly",
        }
