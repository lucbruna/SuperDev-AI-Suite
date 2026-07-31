from __future__ import annotations

import ast
import re
from typing import Any

from .config import ReviewConfig


class ReviewEngine:
    def __init__(self, config: ReviewConfig | None = None):
        self._config = config or ReviewConfig()

    async def review_pr(self, files: list[dict[str, Any]], diff: str) -> dict[str, Any]:
        comments: list[dict[str, Any]] = []
        summary_issues: list[str] = []
        score = 10

        for file in files:
            filename = file.get("filename", "")
            patch = file.get("patch", "")

            if filename.endswith((".py", ".js", ".ts", ".tsx", ".jsx")):
                file_comments, file_issues, file_score = self._review_code_file(filename, patch, file.get("status", ""))
                comments.extend(file_comments)
                summary_issues.extend(file_issues)
                score = max(0, score - file_score)
            elif filename.endswith((".yaml", ".yml", ".json", ".toml")):
                config_comments, config_issues = self._review_config_file(filename, patch)
                comments.extend(config_comments)
                summary_issues.extend(config_issues)
                score = max(0, score - len(config_issues))

        conclusion = "success" if score >= 7 else ("neutral" if score >= 4 else "failure")
        summary = self._build_summary(summary_issues, score, len(files))

        return {
            "conclusion": conclusion,
            "score": score,
            "summary": summary,
            "comments": comments[:20],
            "total_issues": len(summary_issues),
        }

    def _review_code_file(self, filename: str, patch: str, status: str) -> tuple[list[dict], list[str], int]:
        comments: list[dict] = []
        issues: list[str] = []
        score = 0

        if status == "deleted":
            return comments, issues, 0

        rules = self._config.get_rules_for_file(filename)

        for rule in rules:
            matches = self._apply_rule(rule, patch)
            for match in matches:
                issues.append(f"{filename}: {match['message']}")
                score += rule.get("severity", 1)
                if rule.get("severity", 1) >= 3:
                    comments.append({
                        "path": filename,
                        "body": f"**{rule['name']}**: {match['message']}\n\n{match.get('suggestion', '')}",
                        "line": match.get("line", 1),
                    })

        if filename.endswith(".py"):
            py_issues = self._analyze_python_ast(patch)
            for pi in py_issues:
                issues.append(f"{filename}: {pi['message']}")
                score += pi.get("severity", 1)
                if pi.get("severity", 1) >= 2:
                    comments.append({
                        "path": filename,
                        "body": f"**Python**: {pi['message']}",
                        "line": pi.get("line", 1),
                    })

        return comments, issues, min(score, 5)

    def _apply_rule(self, rule: dict[str, Any], patch: str) -> list[dict[str, Any]]:
        matches = []
        pattern = rule.get("pattern", "")
        if not pattern:
            return matches
        for i, line in enumerate(patch.split("\n"), 1):
            if line.startswith("+") and re.search(pattern, line):
                matches.append({
                    "line": i,
                    "message": rule.get("message", "Potential issue"),
                    "suggestion": rule.get("suggestion", ""),
                })
        return matches[:3]

    def _analyze_python_ast(self, patch: str) -> list[dict[str, Any]]:
        issues = []
        added_lines = []
        for line in patch.split("\n"):
            if line.startswith("+") and not line.startswith("+++"):
                added_lines.append(line[1:])

        source = "\n".join(added_lines)
        if not source.strip():
            return issues

        try:
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if len(node.body) > 50:
                        issues.append({"message": f"Function '{node.name}' has {len(node.body)} lines, consider refactoring", "line": node.lineno or 1, "severity": 2})
                if isinstance(node, ast.Try):
                    if not any(isinstance(h, ast.ExceptHandler) and h.name for h in node.handlers):
                        issues.append({"message": "Broad exception handler, consider catching specific exceptions", "line": node.lineno or 1, "severity": 3})
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    if node.func.attr == "execute" and isinstance(node.func.value, ast.Name) and node.func.value.id in ("os", "subprocess"):
                        issues.append({"message": "Shell execution detected, validate inputs to prevent injection", "line": node.lineno or 1, "severity": 4})
        except SyntaxError:
            issues.append({"message": "Added code has syntax errors", "line": 1, "severity": 5})

        return issues

    def _review_config_file(self, filename: str, patch: str) -> tuple[list[dict], list[str]]:
        issues = []
        comments = []
        added_lines = [l[1:] for l in patch.split("\n") if l.startswith("+") and not l.startswith("+++")]

        for line in added_lines:
            if "password" in line.lower() or "secret" in line.lower() or "api_key" in line.lower():
                if "****" not in line and len(line.split(":")) > 1:
                    val = line.split(":", 1)[1].strip().strip('"').strip("'")
                    if val and val != "****" and len(val) > 3:
                        issues.append(f"{filename}: Possible secret exposed in config")
                        comments.append({"path": filename, "body": "**Security**: Possible secret/API key exposed in config file", "line": 1})

        return comments, issues

    def _build_summary(self, issues: list[str], score: int, file_count: int) -> str:
        if not issues:
            return f"✅ **SuperDev Review**: Score {score}/10 — No issues found across {file_count} files."

        top = issues[:5]
        bullet = "\n".join(f"- {i}" for i in top)
        rest = len(issues) - 5
        more = f"\n+ {rest} more issues" if rest > 0 else ""
        return (
            f"### SuperDev Code Review\n\n"
            f"**Score**: {score}/10\n"
            f"**Files reviewed**: {file_count}\n"
            f"**Issues found**: {len(issues)}\n\n"
            f"**Top issues:**\n{bullet}{more}"
        )
