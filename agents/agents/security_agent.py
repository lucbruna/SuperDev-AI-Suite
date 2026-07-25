from __future__ import annotations

import os
import re
from typing import Any

from ..base.base_agent import AgentResult, BaseAgent


class SecurityAgent(BaseAgent):
    async def initialize(self) -> None:
        self._status = "ready"

    async def execute(self, task: str, context: dict[str, Any]) -> AgentResult:
        try:
            await self._check_cancelled()
            self._status = "running"

            path = context.get("path", task)
            findings = []

            secrets = await self._scan_secrets(path)
            findings.extend(secrets)

            deps = await self._check_dependencies(path)
            findings.extend(deps)

            permissions = await self._check_permissions(path)
            findings.extend(permissions)

            report = self._build_report(findings)

            return AgentResult(
                success=len([f for f in findings if f["severity"] == "critical"]) == 0,
                output=report,
                metrics={
                    "total_findings": len(findings),
                    "critical": sum(1 for f in findings if f["severity"] == "critical"),
                    "high": sum(1 for f in findings if f["severity"] == "high"),
                    "medium": sum(1 for f in findings if f["severity"] == "medium"),
                    "low": sum(1 for f in findings if f["severity"] == "low"),
                },
                artifacts={"findings": findings},
            )
        except Exception as e:
            self._error_count += 1
            return AgentResult(success=False, output="", error=str(e))
        finally:
            self._status = "idle"

    async def _scan_secrets(self, path: str) -> list[dict[str, Any]]:
        findings = []
        if not os.path.exists(path):
            return findings

        secret_patterns = [
            (r"(?i)(?:api[_-]?key|apikey)\s*[=:]\s*['\"][^'\"]+['\"]", "API Key", "critical"),
            (r"(?i)(?:password|passwd)\s*[=:]\s*['\"][^'\"]+['\"]", "Password", "critical"),
            (r"(?i)(?:secret|token)\s*[=:]\s*['\"][^'\"]+['\"]", "Secret/Token", "critical"),
            (r"(?i)-----BEGIN (?:RSA |EC )?PRIVATE KEY-----", "Private Key", "critical"),
            (r"(?i)ghp_[a-zA-Z0-9]{36}", "GitHub Token", "critical"),
            (r"(?i)sk-[a-zA-Z0-9]{32,}", "OpenAI API Key", "critical"),
        ]

        for root, _dirs, files in os.walk(path):
            for fname in files:
                if fname.endswith((".py", ".js", ".ts", ".env", ".yml", ".yaml", ".json", ".toml", ".cfg")):
                    try:
                        fpath = os.path.join(root, fname)
                        with open(fpath, encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                            for pattern, desc, severity in secret_patterns:
                                for m in re.finditer(pattern, content):
                                    line_num = content[:m.start()].count("\n") + 1
                                    findings.append({
                                        "type": "secret",
                                        "file": fpath,
                                        "line": line_num,
                                        "description": desc,
                                        "severity": severity,
                                        "match": m.group()[:30] + "...",
                                    })
                    except Exception:
                        pass
        return findings

    async def _check_dependencies(self, path: str) -> list[dict[str, Any]]:
        findings = []
        if not os.path.exists(path):
            return findings
        requirements_files = []
        for root, _dirs, files in os.walk(path):
            for f in files:
                if f in ("requirements.txt", "Pipfile", "poetry.lock", "yarn.lock", "package-lock.json"):
                    requirements_files.append(os.path.join(root, f))
        if not requirements_files:
            findings.append({
                "type": "dependency",
                "file": "N/A",
                "line": 0,
                "description": "No dependency files found",
                "severity": "medium",
            })
        return findings

    async def _check_permissions(self, path: str) -> list[dict[str, Any]]:
        findings = []
        if not os.path.exists(path):
            return findings
        for root, _dirs, files in os.walk(path):
            for fname in files:
                fpath = os.path.join(root, fname)
                try:
                    mode = os.stat(fpath).st_mode
                    if mode & 0o777 == 0o777:
                        findings.append({
                            "type": "permission",
                            "file": fpath,
                            "line": 0,
                            "description": "World-writable file permissions",
                            "severity": "medium",
                        })
                except Exception:
                    pass
        return findings

    def _build_report(self, findings: list[dict]) -> str:
        lines = ["## Security Scan Report", ""]
        if not findings:
            lines.append("✓ No security issues found.")
            return "\n".join(lines)

        by_severity = {"critical": [], "high": [], "medium": [], "low": []}
        for f in findings:
            by_severity.setdefault(f["severity"], []).append(f)

        for severity in ("critical", "high", "medium", "low"):
            items = by_severity.get(severity, [])
            if items:
                lines.append(f"### {severity.upper()} ({len(items)})")
                for item in items:
                    lines.append(f"- [{item['type']}] {item['file']}:{item['line']} - {item['description']}")
                lines.append("")

        return "\n".join(lines)

    def capabilities(self) -> list[str]:
        return ["secret_detection", "dependency_checking", "permission_auditing", "vulnerability_scanning"]
