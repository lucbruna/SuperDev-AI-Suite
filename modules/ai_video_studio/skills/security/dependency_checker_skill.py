"""Dependency checker skill — security posture of dependencies."""
from __future__ import annotations
from typing import Any


class DependencyCheckerSkill:
    """Review dependency security: CVEs, versions, and provenance."""

    skill_id = "dependency_checker"
    skill_name = "Dependency Checker"
    skill_version = "1.0.0"
    skill_description = "Dependency security review: CVEs, versions, provenance."
    skill_category = "security"
    skill_tags = ["security", "dependencies", "cve", "supply-chain"]
    skill_permissions = ["content:plan"]

    def __init__(self) -> None:
        pass

    async def __call__(
        self,
        project: str,
        *,
        ecosystem: str = "python",
        language: str = "en",
    ) -> dict[str, Any]:
        """Return a dependency security review plan."""
        return {
            "project": project,
            "ecosystem": ecosystem,
            "language": language,
            "checks": [
                {"check": "known CVEs", "action": "Match lockfile versions against advisory databases."},
                {"check": "outdated major", "action": "Flag majors behind by more than one release."},
                {"check": "abandoned", "action": "Flag packages with no releases in 18+ months."},
                {"check": "provenance", "action": "Verify the package source and publisher."},
                {"check": "transitive risk", "action": "Review the dependency tree for surprises."},
            ],
            "response": ["update with care", "pin exact versions", "add scanner to CI"],
            "note": "Treat unmaintained or typosquatting packages as high risk.",
        }
