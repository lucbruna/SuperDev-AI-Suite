from __future__ import annotations

from typing import Any

from backend.issue_to_pr.template import PRTemplateEngine


class PRAgent:
    def __init__(self):
        self._template_engine = PRTemplateEngine()

    async def generate_from_issue(self, issue: dict[str, Any]) -> dict[str, Any]:
        title = issue.get("title", "Untitled")
        body = issue.get("body", "")
        number = issue.get("number", 0)
        return {
            "issue_number": number,
            "title": title,
            "branch": self._template_engine.generate_branch_name(title, number),
            "commit_message": self._template_engine.generate_commit_message(title, number),
            "pr_body": self._template_engine.generate(title, body),
        }

    async def analyze_issue_complexity(self, issue: dict[str, Any]) -> dict[str, Any]:
        title = issue.get("title", "")
        body = issue.get("body", "") or ""
        labels = [l.get("name", "") for l in issue.get("labels", [])]

        word_count = len(body.split())
        has_ac = bool(any(line.strip().startswith("- [") for line in body.split("\n")))
        has_technical = "implementation" in body.lower() or "technical" in body.lower()
        label_score = 0
        for label in labels:
            if label.lower() in ("bug", "critical", "blocker"):
                label_score += 3
            elif label.lower() in ("enhancement", "feature", "improvement"):
                label_score += 1

        score = min(10, (word_count // 50) + (1 if has_ac else 0) + (1 if has_technical else 0) + label_score)
        return {
            "complexity_score": score,
            "estimated_files": max(1, score // 2),
            "estimated_hours": max(0.5, score * 0.5),
            "needs_review": score > 6,
            "labels": labels,
            "has_acceptance_criteria": has_ac,
        }

    async def suggest_assignee(self, issue: dict[str, Any], team: list[dict[str, Any]]) -> str | None:
        issue_labels = [l.get("name", "").lower() for l in issue.get("labels", [])]
        best_match = None
        best_score = -1

        for member in team:
            score = 0
            member_skills = [s.lower() for s in member.get("skills", [])]
            for label in issue_labels:
                if label in member_skills:
                    score += 2
                if any(skill in label for skill in member_skills):
                    score += 1
            current_load = member.get("current_prs", 0)
            score -= current_load * 0.5
            if score > best_score:
                best_score = score
                best_match = member.get("login")

        return best_match