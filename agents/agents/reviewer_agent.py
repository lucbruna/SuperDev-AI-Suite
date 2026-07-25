from __future__ import annotations

import os
import re
from typing import Any

from ..base.base_agent import AgentResult, BaseAgent


class ReviewerAgent(BaseAgent):
    async def initialize(self) -> None:
        self._status = "ready"

    async def execute(self, task: str, context: dict[str, Any]) -> AgentResult:
        try:
            await self._check_cancelled()
            self._status = "running"

            file_path = context.get("file_path", task)
            code = await self._read_file(file_path)

            if not code and not file_path:
                return AgentResult(success=False, output="", error="No file path or code provided")

            issues = []
            if code:
                issues.extend(self._check_style(code))
                issues.extend(self._check_security(code))
                issues.extend(self._check_bugs(code))
                issues.extend(self._check_complexity(code))

            report = self._generate_report(file_path, code, issues)

            return AgentResult(
                success=len(issues) == 0,
                output=report,
                metrics={"issues_found": len(issues), "file_reviewed": file_path or "inline"},
                artifacts={"issues": issues, "report": report},
            )
        except Exception as e:
            self._error_count += 1
            return AgentResult(success=False, output="", error=str(e))
        finally:
            self._status = "idle"

    async def _read_file(self, path: str) -> str:
        if not path or not os.path.isfile(path):
            return ""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return ""

    def _check_style(self, code: str) -> list[dict[str, Any]]:
        issues = []
        lines = code.split("\n")
        for i, line in enumerate(lines, 1):
            if len(line) > 100:
                issues.append({"type": "style", "line": i, "message": f"Line too long ({len(line)} > 100)", "severity": "warning"})
            if line.strip().endswith(" ") or line.strip().endswith("\t"):
                issues.append({"type": "style", "line": i, "message": "Trailing whitespace", "severity": "info"})
            if "\t" in line:
                issues.append({"type": "style", "line": i, "message": "Tab character used, use spaces", "severity": "warning"})
        return issues

    def _check_security(self, code: str) -> list[dict[str, Any]]:
        issues = []
        patterns = [
            (r"(?i)password\s*=\s*['\"][^'\"]+['\"]", "Hardcoded password", "critical"),
            (r"(?i)secret\s*=\s*['\"][^'\"]+['\"]", "Hardcoded secret", "critical"),
            (r"(?i)api[_-]?key\s*=\s*['\"][^'\"]+['\"]", "Hardcoded API key", "critical"),
            (r"(?i)exec\(|eval\(|__import__\(", "Use of exec/eval", "high"),
            (r"(?i)subprocess\.call|subprocess\.Popen", "Subprocess usage", "medium"),
        ]
        for pattern, message, severity in patterns:
            for m in re.finditer(pattern, code):
                line_num = code[:m.start()].count("\n") + 1
                issues.append({"type": "security", "line": line_num, "message": message, "severity": severity})
        return issues

    def _check_bugs(self, code: str) -> list[dict[str, Any]]:
        issues = []
        lines = code.split("\n")
        for i, line in enumerate(lines, 1):
            if "except:" in line and "# noqa" not in line:
                issues.append({"type": "bug", "line": i, "message": "Bare except clause", "severity": "high"})
            if "TODO" in line.upper():
                issues.append({"type": "bug", "line": i, "message": "TODO left in code", "severity": "info"})
        return issues

    def _check_complexity(self, code: str) -> list[dict[str, Any]]:
        issues = []
        lines = code.split("\n")
        func_lines = 0
        for i, line in enumerate(lines, 1):
            if line.strip().startswith("def ") or line.strip().startswith("class "):
                func_lines = 1
            elif func_lines > 0:
                func_lines += 1
                if func_lines > 80:
                    issues.append({"type": "complexity", "line": i, "message": "Function/class too long", "severity": "warning"})
                    func_lines = 0
        return issues

    def _generate_report(self, file_path: str, code: str, issues: list) -> str:
        newline_count = code.count("\n") if code else 0
        lines = [
            f"## Code Review Report",
            f"**File:** {file_path or 'inline code'}",
            f"**Lines:** {newline_count}",
            f"**Issues Found:** {len(issues)}",
            "",
        ]
        for issue in issues:
            lines.append(f"- [{issue['severity'].upper()}] Line {issue['line']}: {issue['message']}")
        if not issues:
            lines.append("✓ No issues found. Code looks clean!")
        return "\n".join(lines)

    def capabilities(self) -> list[str]:
        return ["code_review", "style_checking", "security_scanning", "bug_detection"]
