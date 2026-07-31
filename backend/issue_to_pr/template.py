from __future__ import annotations

from typing import Any


class PRTemplateEngine:
    def generate(self, title: str, body: str) -> str:
        description = self._parse_issue_body(body)
        return f"""## Summary
{description.get("summary", title)}

## Changes
{self._generate_changes_section(description)}

## Testing
- [ ] Unit tests pass
- [ ] Manual testing completed

## Related Issue
Closes #{description.get("issue_number", "0")}

## Checklist
- [ ] Code follows project conventions
- [ ] Documentation updated
- [ ] No breaking changes introduced
"""

    def _parse_issue_body(self, body: str) -> dict[str, Any]:
        lines = body.strip().split("\n")
        result: dict[str, Any] = {"summary": "", "acceptance_criteria": [], "technical_notes": ""}
        current_section = "summary"

        for line in lines:
            stripped = line.strip()
            lower = stripped.lower()
            if lower.startswith("## ") or stripped.startswith("### "):
                if "acceptance" in lower or "criteria" in lower:
                    current_section = "acceptance_criteria"
                elif "technical" in lower or "implementation" in lower:
                    current_section = "technical_notes"
                elif "summary" in lower or "description" in lower:
                    current_section = "summary"
                else:
                    current_section = "summary"
                continue

            if stripped.startswith("- [") and current_section == "acceptance_criteria":
                result["acceptance_criteria"].append(stripped)
            elif current_section == "summary" and stripped:
                result["summary"] += stripped + " "
            elif current_section == "technical_notes" and stripped:
                result["technical_notes"] += stripped + " "

        result["summary"] = result["summary"].strip()
        return result

    def _generate_changes_section(self, description: dict[str, Any]) -> str:
        changes = []
        if description.get("summary"):
            changes.append(f"- Implement: {description['summary'][:100]}")
        for ac in description.get("acceptance_criteria", [])[:5]:
            changes.append(f"- {ac}")
        if description.get("technical_notes"):
            changes.append(f"- {description['technical_notes'][:100]}")
        if not changes:
            changes.append("- Implement changes as described in issue")
        return "\n".join(changes)

    def generate_branch_name(self, title: str, issue_number: int) -> str:
        import re

        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:40]
        return f"auto/issue-{issue_number}-{slug}"

    def generate_commit_message(self, title: str, issue_number: int) -> str:
        return f"feat: {title[:60]} (closes #{issue_number})"
